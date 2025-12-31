# economic/ecommerce/models/wishlist.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .product import Product


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ecom_wishlist",
        verbose_name=_("Utilisateur"),
    )
    created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Liste de souhaits")
        verbose_name_plural = _("Listes de souhaits")

    def __str__(self):
        return f"Wishlist({self.user_id})"

    @property
    def items_count(self) -> int:
        return self.items.count()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Liste de souhaits"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
        verbose_name=_("Produit"),
    )
    created_at = models.DateTimeField(_("Ajouté le"), default=timezone.now)

    class Meta:
        verbose_name = _("Produit favori")
        verbose_name_plural = _("Produits favoris")
        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                name="unique_product_per_wishlist"
            )
        ]

    def __str__(self):
        return self.product.safe_translation_getter("name", any_language=True) or "Produit"





# # economic/ecommerce/models/wishlist.py

# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from .product import Product


# class Wishlist(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="ecom_wishlist",
#         verbose_name=_("Utilisateur"),
#     )
#     created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Liste de souhaits")
#         verbose_name_plural = _("Listes de souhaits")

#     def __str__(self):
#         return f"Wishlist({self.user_id})"

#     @property
#     def items_count(self) -> int:
#         return self.items.count()


# class WishlistItem(models.Model):
#     wishlist = models.ForeignKey(
#         Wishlist,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Liste de souhaits"),
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="wishlisted_by",
#         verbose_name=_("Produit"),
#     )
#     created_at = models.DateTimeField(_("Ajouté le"), default=timezone.now)

#     class Meta:
#         verbose_name = _("Produit favori")
#         verbose_name_plural = _("Produits favoris")
#         unique_together = ("wishlist", "product")

#     def __str__(self):
#         name = self.product.safe_translation_getter("name", any_language=True)
#         return f"{name}"
