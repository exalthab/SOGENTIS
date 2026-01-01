# /economic/ecommerce/models/wishlist_item.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from .wishlist import Wishlist
from .product import Product


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Wishlist"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name=_("Produit"),
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Ajouté le"),
    )

    class Meta:
        verbose_name = _("Élément de wishlist")
        verbose_name_plural = _("Éléments de wishlist")

        # ✅ Bonne pratique moderne (au lieu de unique_together)
        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                name="unique_product_per_wishlist",
            )
        ]

    def __str__(self):
        return f"{self.product} → {self.wishlist}"







# # sogentis_apps/economic/ecommerce/models/wishlist_item.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .wishlist import Wishlist
# from .product import Product


# class WishlistItem(models.Model):
#     wishlist = models.ForeignKey(
#         Wishlist,
#         on_delete=models.CASCADE,
#         related_name="items",
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="wishlist_items",
#     )
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Élément de wishlist")
#         verbose_name_plural = _("Éléments de wishlist")
#         unique_together = ("wishlist", "product")
#         # app_label = "economic_ecommerce"  # ⚡ correspond au label dans EcommerceConfig


#     def __str__(self):
#         return f"{self.product} → {self.wishlist}"
