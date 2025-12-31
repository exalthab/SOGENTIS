# sogentis_apps/economic/ecommerce/models/wishlist.py

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

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créée le"),
    )

    class Meta:
        verbose_name = _("Liste de souhaits")
        verbose_name_plural = _("Listes de souhaits")

    def __str__(self):
        return f"Wishlist ({self.user})"






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

