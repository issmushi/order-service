from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from apps.products.models import Goods, Category
from apps.promos.models import PromoCode, PromoUsage


User = get_user_model()


class TestCreateOrder(APITestCase):
    """Tests for order creation API."""

    def setUp(self):
        """Prepare test data: user, goods, categories and promo."""
        self.url = "/api/orders/"

        self.user = User.objects.create(username="test_user")

        self.category = Category.objects.create(name="Allowed")
        self.other_category = Category.objects.create(name="Other")

        self.good = Goods.objects.create(
            name="Good",
            price=Decimal("100"),
            category=self.category,
            is_excluded_from_promos=False,
        )

        self.excluded_good = Goods.objects.create(
            name="Excluded",
            price=Decimal("200"),
            category=self.category,
            is_excluded_from_promos=True,
        )

        self.other_category_good = Goods.objects.create(
            name="Other Cat",
            price=Decimal("300"),
            category=self.other_category,
            is_excluded_from_promos=False,
        )

        self.promo = PromoCode.objects.create(
            code="PROMO",
            discount_percent=Decimal("10"),
            expires_at=timezone.now() + timezone.timedelta(days=1),
            max_usages=1,
        )

        self.promo.categories.add(self.category)

    def test_success(self):
        """Order should be created successfully with valid data."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
            "promo_code": "PROMO",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_goods_not_found(self):
        """Should return error if goods do not exist."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": 999, "quantity": 1}],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_goods(self):
        """Should return error if goods list is empty."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

