# economic/ecommerce/models/cart.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("Utilisateur"),
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créé le"),
    )

    def __str__(self):
        return f"Panier de {self.user}"

    @property
    def total_amount(self):
        # ⚠️ utilise CartItem via related_name="items"
        return sum(item.total_price for item in self.items.all())







# # /economic/ecommerce/models/cart.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="cart",          # 🔑 simple, unique
#         verbose_name=_("Utilisateur"),
#         null=True,
#         blank=True,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     def __str__(self):
#         return f"Panier #{self.pk}"
