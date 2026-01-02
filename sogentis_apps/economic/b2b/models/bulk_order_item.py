from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _

from .bulk_order import BulkOrder
from economic.ecommerce.models.product import Product


class BulkOrderItem(models.Model):
    bulk_order = models.ForeignKey(
        BulkOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Commande en gros"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="bulk_order_items",
        verbose_name=_("Produit"),
    )

    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantité"))

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Prix unitaire"))

    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=Decimal("0.00"),
        verbose_name=_("Total"),
    )

    class Meta:
        verbose_name = _("Ligne de commande en gros")
        verbose_name_plural = _("Lignes de commande en gros")
        constraints = [
            models.UniqueConstraint(fields=["bulk_order", "product"], name="unique_product_per_bulk_order")
        ]

    def save(self, *args, **kwargs):
        self.total_price = (self.unit_price or Decimal("0.00")) * Decimal(self.quantity or 0)
        super().save(*args, **kwargs)
        if self.bulk_order_id:
            self.bulk_order.recalc_total(save=True)

    def delete(self, *args, **kwargs):
        bulk = self.bulk_order
        super().delete(*args, **kwargs)
        if bulk:
            bulk.recalc_total(save=True)

    def __str__(self):
        return f"{self.product} × {self.quantity}"









# # /economic/b2b/models/bulk_order_item.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .bulk_order import BulkOrder
# from economic.ecommerce.models.product import Product


# class BulkOrderItem(models.Model):
#     bulk_order = models.ForeignKey(
#         BulkOrder,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Commande en gros"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.PROTECT,
#         related_name="bulk_order_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(
#         default=1,
#         verbose_name=_("Quantité"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix unitaire"),
#     )

#     total_price = models.DecimalField(
#         max_digits=14,
#         decimal_places=2,
#         editable=False,
#         verbose_name=_("Total"),
#     )

#     class Meta:
#         verbose_name = _("Ligne de commande en gros")
#         verbose_name_plural = _("Lignes de commande en gros")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["bulk_order", "product"],
#                 name="unique_product_per_bulk_order",
#             )
#         ]

#     def save(self, *args, **kwargs):
#         self.total_price = (self.unit_price or 0) * (self.quantity or 0)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"








# # /economic/b2b/models/bulk_order_item.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models.bulk_order import BulkOrder
# from economic.ecommerce.models import Product


# class BulkOrderItem(models.Model):
#     bulk_order = models.ForeignKey(
#         BulkOrder,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Commande en gros"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.PROTECT,
#         related_name="bulk_order_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(verbose_name=_("Quantité"))

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix unitaire"),
#     )

#     total_price = models.DecimalField(
#         max_digits=14,
#         decimal_places=2,
#         editable=False,
#         verbose_name=_("Total"),
#     )

#     class Meta:
#         verbose_name = _("Ligne de commande en gros")
#         verbose_name_plural = _("Lignes de commande en gros")
#         unique_together = ("bulk_order", "product")

#     def save(self, *args, **kwargs):
#         self.total_price = self.unit_price * self.quantity
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"
