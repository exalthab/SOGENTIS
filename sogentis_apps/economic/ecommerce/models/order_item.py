# /economic/ecommerce/models/order_item.py
from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .order import Order
from .product import Product


D0 = Decimal("0.00")


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

    # ✅ Snapshots (prod): gardent l'info même si le produit évolue
    product_sku = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name=_("SKU (snapshot)"),
    )

    product_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Nom produit (snapshot)"),
    )

    quantity = models.PositiveIntegerField(verbose_name=_("Quantité"))

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Prix unitaire"),
    )

    currency = models.CharField(
        max_length=10,
        default="XOF",
        db_index=True,
        verbose_name=_("Devise"),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Créé le"),
        editable=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Mis à jour le"),
    )

    class Meta:
        verbose_name = _("Article de commande")
        verbose_name_plural = _("Articles de commande")
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            # ✅ Django 5.2+: utiliser "condition" (check est déprécié)
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="chk_orderitem_qty_gt_0",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="chk_orderitem_unitprice_gte_0",
            ),
        ]

    def __str__(self) -> str:
        label = self.product_name or (str(self.product) if self.product_id else _("Produit"))
        return f"{label} × {self.quantity}"

    # -------------------------
    # Validations prod
    # -------------------------
    def clean(self):
        super().clean()

        if not self.quantity or self.quantity < 1:
            raise ValidationError({"quantity": _("La quantité doit être au moins 1.")})

        if self.unit_price is None:
            raise ValidationError({"unit_price": _("Le prix unitaire est obligatoire.")})

        if self.unit_price is not None and self.unit_price < 0:
            raise ValidationError({"unit_price": _("Le prix unitaire ne peut pas être négatif.")})

        if self.currency:
            self.currency = self.currency.strip().upper()

    # -------------------------
    # Save (snapshots + normalisation)
    # -------------------------
    def save(self, *args, **kwargs):
        # normalise currency
        if self.currency:
            self.currency = self.currency.strip().upper()

        # ✅ aligne la devise sur la commande si nécessaire
        order_currency = getattr(self.order, "currency", None)
        if order_currency and not self.currency:
            self.currency = (order_currency or "").strip().upper()

        # ✅ snapshots auto si vides
        if self.product_id:
            if not self.product_sku:
                self.product_sku = (getattr(self.product, "sku", "") or "").strip().upper()
            if not self.product_name:
                self.product_name = self.product.safe_translation_getter("name", any_language=True) or ""

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self) -> Decimal:
        try:
            return (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"))
        except Exception:
            return D0

    @property
    def line_total(self) -> Decimal:
        # Compat template: order_detail.html utilise item.line_total
        return self.total_price


# # /economic/ecommerce/models/order_item.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils import timezone
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
#         related_name="order_items",
#         verbose_name=_("Produit"),
#     )

#     product_sku = models.CharField(
#         max_length=100,
#         blank=True,
#         db_index=True,
#         verbose_name=_("SKU (snapshot)"),
#     )

#     product_name = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Nom produit (snapshot)"),
#     )

#     quantity = models.PositiveIntegerField(verbose_name=_("Quantité"))

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix unitaire"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         verbose_name=_("Créé le"),
#         editable=False,
#     )

#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Article de commande")
#         verbose_name_plural = _("Articles de commande")
#         ordering = ["id"]
#         indexes = [
#             models.Index(fields=["order"]),
#             models.Index(fields=["product"]),
#             models.Index(fields=["created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=models.Q(quantity__gt=0), name="chk_orderitem_qty_gt_0"),
#             models.CheckConstraint(check=models.Q(unit_price__gte=0), name="chk_orderitem_unitprice_gte_0"),
#         ]

#     def __str__(self):
#         label = self.product_name or (str(self.product) if self.product_id else _("Produit"))
#         return f"{label} × {self.quantity}"

#     def clean(self):
#         super().clean()

#         if not self.quantity or self.quantity < 1:
#             raise ValidationError({"quantity": _("La quantité doit être au moins 1.")})

#         if self.unit_price is None:
#             raise ValidationError({"unit_price": _("Le prix unitaire est obligatoire.")})

#         if self.unit_price is not None and self.unit_price < 0:
#             raise ValidationError({"unit_price": _("Le prix unitaire ne peut pas être négatif.")})

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#     def save(self, *args, **kwargs):
#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         # ✅ aligne la devise sur la commande si tu ajoutes currency côté Order plus tard
#         order_currency = getattr(self.order, "currency", None)
#         if order_currency and not self.currency:
#             self.currency = (order_currency or "").strip().upper()

#         # ✅ snapshots auto (et toujours figés si vides)
#         if self.product_id:
#             if not self.product_sku:
#                 self.product_sku = (getattr(self.product, "sku", "") or "").strip().upper()
#             if not self.product_name:
#                 self.product_name = self.product.safe_translation_getter("name", any_language=True) or ""

#         self.full_clean()
#         super().save(*args, **kwargs)

#     @property
#     def total_price(self) -> Decimal:
#         return (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"))





# # /economic/ecommerce/models/order_item.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils import timezone
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
#         on_delete=models.PROTECT,  # 🔒 ne jamais supprimer un produit déjà vendu
#         related_name="order_items",
#         verbose_name=_("Produit"),
#     )

#     # ✅ Snapshots (prod): garde l'info même si le produit est modifié/supprimé logique
#     product_sku = models.CharField(
#         max_length=100,
#         blank=True,
#         db_index=True,
#         verbose_name=_("SKU (snapshot)"),
#     )

#     product_name = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Nom produit (snapshot)"),
#     )

#     quantity = models.PositiveIntegerField(
#         verbose_name=_("Quantité"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix unitaire"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         verbose_name=_("Créé le"),
#         editable=False,
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Article de commande")
#         verbose_name_plural = _("Articles de commande")
#         ordering = ["id"]
#         indexes = [
#             models.Index(fields=["order"]),
#             models.Index(fields=["product"]),
#             models.Index(fields=["created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=models.Q(quantity__gt=0), name="chk_orderitem_qty_gt_0"),
#             models.CheckConstraint(check=models.Q(unit_price__gte=0), name="chk_orderitem_unitprice_gte_0"),
#         ]

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"

#     def clean(self):
#         super().clean()

#         if not self.quantity or self.quantity < 1:
#             raise ValidationError({"quantity": _("La quantité doit être au moins 1.")})

#         if self.unit_price is None:
#             raise ValidationError({"unit_price": _("Le prix unitaire est obligatoire.")})

#         if self.unit_price is not None and self.unit_price < 0:
#             raise ValidationError({"unit_price": _("Le prix unitaire ne peut pas être négatif.")})

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#     def save(self, *args, **kwargs):
#         # Normalisation devise
#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         # Snapshots auto si vides
#         if self.product_id:
#             if not self.product_sku:
#                 self.product_sku = (getattr(self.product, "sku", "") or "").strip().upper()
#             if not self.product_name:
#                 self.product_name = self.product.safe_translation_getter("name", any_language=True) or ""

#         self.full_clean()
#         super().save(*args, **kwargs)

#     @property
#     def total_price(self) -> Decimal:
#         """Prix total pour cette ligne de commande"""
#         return (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"))






# # /economic/ecommerce/models/order_item.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

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
#         on_delete=models.PROTECT,  # 🔒 ne jamais supprimer un produit déjà vendu
#         related_name="order_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(
#         verbose_name=_("Quantité"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,  # Permet des prix unitaires élevés
#         decimal_places=2,
#         verbose_name=_("Prix unitaire"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         verbose_name=_("Créé le"),
#         editable=False,
#     )

#     class Meta:
#         verbose_name = _("Article de commande")
#         verbose_name_plural = _("Articles de commande")
#         ordering = ["id"]
#         indexes = [
#             models.Index(fields=["order"]),
#         ]

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"

#     @property
#     def total_price(self):
#         """Prix total pour cette ligne de commande"""
#         return self.unit_price * self.quantity






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
