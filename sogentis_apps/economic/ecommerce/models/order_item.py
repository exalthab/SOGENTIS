# /economic/ecommerce/models/order_item.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .order import Order
from .product import Product


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name=_("Commande"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # 🔒 ne jamais supprimer un produit déjà vendu
        related_name="order_items",
        verbose_name=_("Produit"),
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantité"),
    )

    unit_price = models.DecimalField(
        max_digits=12,  # Permet des prix unitaires élevés
        decimal_places=2,
        verbose_name=_("Prix unitaire"),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Créé le"),
        editable=False,
    )

    class Meta:
        verbose_name = _("Article de commande")
        verbose_name_plural = _("Articles de commande")
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    @property
    def total_price(self):
        """Prix total pour cette ligne de commande"""
        return self.unit_price * self.quantity






# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .order import Order
# from .product import Product


# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order,
#         related_name="items",
#         on_delete=models.CASCADE,
#         verbose_name=_("Commande"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.PROTECT,
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(_("Quantité"))

#     unit_price = models.DecimalField(
#         _("Prix unitaire"),
#         max_digits=10,
#         decimal_places=2,
#     )

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"

#     @property
#     def total_price(self):
#         return self.unit_price * self.quantity






# # /economic/ecommerce/models/order_item.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .order import Order
# from .product import Product


# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Commande"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.PROTECT,
#         related_name="order_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(
#         verbose_name=_("Quantité"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix unitaire"),
#     )

#     class Meta:
#         verbose_name = _("Article de commande")
#         verbose_name_plural = _("Articles de commande")

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"
