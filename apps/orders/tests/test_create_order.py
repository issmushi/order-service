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

    def test_invalid_promo(self):
        """Should return error if promo code is invalid."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
            "promo_code": "INVALID",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_promo(self):
        """Should return error if promo code is expired."""
        self.promo.expires_at = timezone.now() - timezone.timedelta(days=1)
        self.promo.save()

        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
            "promo_code": "PROMO",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_promo_already_used_by_user(self):
        """Should return error if user already used this promo."""
        PromoUsage.objects.create(user=self.user, promo_code=self.promo)

        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
            "promo_code": "PROMO",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_promo_usage_limit_reached(self):
        """Should return error if promo usage limit reached."""
        other_user = User.objects.create(username="other")
        PromoUsage.objects.create(user=other_user, promo_code=self.promo)

        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
            "promo_code": "PROMO",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_restriction(self):
        """Promo should not apply to goods from other categories."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.other_category_good.id, "quantity": 1}],
            "promo_code": "PROMO",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["discount"], 0)

    def test_excluded_goods(self):
        """Promo should not apply to excluded goods."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [{"good_id": self.excluded_good.id, "quantity": 1}],
            "promo_code": "PROMO",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["discount"], 0)

    def test_user_not_found(self):
        """Should return error if user does not exist."""
        response = self.client.post(self.url, {
            "user_id": 999,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_goods(self):
        """Should allow duplicated goods in request."""
        response = self.client.post(self.url, {
            "user_id": self.user.id,
            "goods": [
                {"good_id": self.good.id, "quantity": 1},
                {"good_id": self.good.id, "quantity": 2},
            ],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

