from django.db import models
from django.conf import settings

from apps.products.models import Goods
from apps.promos.models import PromoCode


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )

    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='orders',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    goods = models.ForeignKey(
        Goods,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.goods} x {self.quantity}"