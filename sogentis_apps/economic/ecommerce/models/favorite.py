# economic/ecommerce/models/favorite.py
from __future__ import annotations

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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))

    class Meta:
        verbose_name = _("Favori")
        verbose_name_plural = _("Favoris")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="uniq_user_product_fav")
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["product", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.product}"

    @classmethod
    def toggle(cls, user, product) -> bool:
        """
        True = favori ajouté, False = favori retiré
        """
        obj, created = cls.objects.get_or_create(user=user, product=product)
        if created:
            return True
        obj.delete()
        return False





# # economic/ecommerce/models/favorite.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .product import Product


# class Favorite(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="ecommerce_favorites",
#         verbose_name=_("Utilisateur"),
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="favorited_by",
#         verbose_name=_("Produit"),
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Favori")
#         verbose_name_plural = _("Favoris")
#         constraints = [
#             models.UniqueConstraint(fields=["user", "product"], name="uniq_user_product_fav")
#         ]

#     def __str__(self):
#         return f"{self.user} ♥ {self.product}"
