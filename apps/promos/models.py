from django.db import models
from apps.products.models import Category


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    expires_at = models.DateTimeField()

    max_usages = models.PositiveIntegerField()

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='promo_codes'
    )

    def __str__(self):
        return self.code