from django.db import models
from django.conf import settings

from apps.products.models import Category


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)

    discount_percent = models.DecimalField(
        max_digits=4,
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


class PromoUsage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='promo_usages'
    )

    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.CASCADE,
        related_name='usages'
    )

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'promo_code'],
                name='unique_user_promo_code'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.promo_code}"