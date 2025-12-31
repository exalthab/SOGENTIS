# economic/ecommerce/models/review.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .product import Product


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Avis produit")
        verbose_name_plural = _("Avis produits")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product} — {self.rating}/5"
