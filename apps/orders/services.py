from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction, IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from apps.orders.models import Order, OrderItem
from apps.products.models import Goods
from apps.promos.models import PromoCode, PromoUsage


User = get_user_model()


@dataclass(frozen=True)
class GoodsInput:
    """Input DTO for order item."""
    good_id: int
    quantity: int


@transaction.atomic
def create_order(
    *,
    user: User,
    goods_data: list[GoodsInput],
    promo_code_str: str | None = None,
) -> dict:
    """
    Create order with optional promo code.

    Validates:
    - goods existence
    - promo code rules (expiration, usage limits, per-user usage)
    - category restrictions
    - excluded goods

    Returns:
        dict: Order data with totals and discounts
    """
    if not goods_data:
        raise ValidationError("Goods list cannot be empty")

    goods_ids = [item.good_id for item in goods_data]
    unique_goods_ids = set(goods_ids)

    goods_qs = Goods.objects.select_related("category").filter(id__in=unique_goods_ids)
    goods_map = {g.id: g for g in goods_qs}

    if len(goods_map) != len(unique_goods_ids):
        raise ValidationError("Some goods not found")

    promo: PromoCode | None = None

    if promo_code_str:
        try:
            promo = (
                PromoCode.objects
                .select_for_update()
                .prefetch_related("categories")
                .get(code=promo_code_str)
            )
        except PromoCode.DoesNotExist:
            raise ValidationError("Invalid promo code")

        if promo.expires_at < timezone.now():
            raise ValidationError("Promo code expired")

        usages_qs = PromoUsage.objects.select_for_update().filter(promo_code=promo)
        usages_count = usages_qs.count()

        if usages_qs.filter(user=user).exists():
            raise ValidationError("Promo already used by user")

        if usages_count >= promo.max_usages:
            raise ValidationError("Promo usage limit reached")

    order = Order.objects.create(
        user=user,
        promo_code=promo,
    )

    discountable_total = Decimal("0")
    non_discountable_total = Decimal("0")
    original_total = Decimal("0")

    promo_categories = set(promo.categories.all()) if promo else set()

    items_data = []

    for item in goods_data:
        goods = goods_map[item.good_id]
        quantity = item.quantity

        item_total = goods.price * quantity
        original_total += item_total

        OrderItem.objects.create(
            order=order,
            goods=goods,
            quantity=quantity,
            price=goods.price,
        )

        item_discount = Decimal("0")

        if goods.is_excluded_from_promos:
            non_discountable_total += item_total

        elif promo_categories and goods.category not in promo_categories:
            non_discountable_total += item_total

        else:
            discountable_total += item_total
            if promo:
                item_discount = promo.discount_percent / Decimal("100")

        item_total_after_discount = item_total * (Decimal("1") - item_discount)

        items_data.append({
            "good_id": goods.id,
            "quantity": quantity,
            "price": goods.price,
            "discount": item_discount,
            "total": item_total_after_discount,
        })

    has_discount = discountable_total > 0

    if promo and has_discount:
        try:
            PromoUsage.objects.create(
                user=user,
                promo_code=promo,
            )
        except IntegrityError:
            raise ValidationError("Promo already used by user")

        discountable_total *= (
            Decimal("1") - promo.discount_percent / Decimal("100")
        )

    total = discountable_total + non_discountable_total

    discount = (
        promo.discount_percent / Decimal("100")
        if promo and has_discount
        else Decimal("0")
    )

    return {
        "user_id": user.id,
        "order_id": order.id,
        "goods": items_data,
        "price": original_total,
        "discount": discount,
        "total": total,
    }