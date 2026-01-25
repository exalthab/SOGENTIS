# economic/ecommerce/models/wishlist.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",  # 🔑 simple et unique
        verbose_name=_("Utilisateur"),
    )

    # ✅ optionnel mais utile : libellé (ex: "Mes envies")
    name = models.CharField(
        max_length=120,
        default="Wishlist",
        verbose_name=_("Nom"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créée le"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Mise à jour le"),
    )

    class Meta:
        verbose_name = _("Liste de souhaits")
        verbose_name_plural = _("Listes de souhaits")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.user})"

    @property
    def items_count(self) -> int:
        # nécessite wishlist_item.py avec related_name="items"
        items = getattr(self, "items", None)
        return items.count() if items is not None else 0




# # economic/ecommerce/models/wishlist.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Wishlist(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="wishlist",  # 🔑 simple et unique
#         verbose_name=_("Utilisateur"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     class Meta:
#         verbose_name = _("Liste de souhaits")
#         verbose_name_plural = _("Listes de souhaits")

#     def __str__(self):
#         return f"Wishlist ({self.user})"






# # economic/ecommerce/models/wishlist.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .product import Product


# class Wishlist(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="ecommerce_wishlist",
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Liste de souhaits")
#         verbose_name_plural = _("Listes de souhaits")
#         # app_label = "economic_ecommerce"


#     def __str__(self):
#         return f"Wishlist {self.user}"

#     @property
#     def products(self):
#         """
#         Accès pratique : wishlist.products.all()
#         """
#         return Product.objects.filter(wishlist_items__wishlist=self)

