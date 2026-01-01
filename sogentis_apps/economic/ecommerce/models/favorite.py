# economic/ecommerce/models/favorite.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .product import Product


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ecommerce_favorites",
        verbose_name=_("Utilisateur"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Produit"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Favori")
        verbose_name_plural = _("Favoris")
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="uniq_user_product_fav")
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
