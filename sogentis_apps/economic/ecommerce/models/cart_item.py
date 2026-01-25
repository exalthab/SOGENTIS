# economic/ecommerce/models/cart_item.py
from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .cart import Cart
from .product import Product


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Panier"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("Produit"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantité"),
    )

    # ✅ Snapshot du prix au moment de l’ajout au panier
    unit_price = models.DecimalField(
        _("Prix unitaire"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ✅ Optionnel mais utile : stocker la devise (si ton Cart a currency)
    currency = models.CharField(
        max_length=5,
        blank=True,
        verbose_name=_("Devise"),
        help_text=_("Optionnel : hérite du panier si vide."),
        db_index=True,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Article du panier")
        verbose_name_plural = _("Articles du panier")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_per_cart",
            )
        ]
        indexes = [
            models.Index(fields=["cart", "created_at"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    # -------------------------
    # Pricing snapshot (prod)
    # -------------------------
    def _resolve_unit_price(self) -> Decimal:
        """
        Choix du prix unitaire :
        - Si ProductPricing existe : effective_unit_price (promo)
        - Sinon : Product.price
        """
        # product_pricing (si ton modèle ProductPricing est branché en OneToOne related_name="pricing")
        pricing = getattr(self.product, "pricing", None)
        if pricing and getattr(pricing, "is_active", True):
            try:
                return pricing.effective_unit_price
            except Exception:
                pass

        # fallback sur Product.price
        try:
            return Decimal(self.product.price)
        except Exception:
            return Decimal("0.00")

    # -------------------------
    # Validations prod
    # -------------------------
    def clean(self):
        super().clean()

        if not self.quantity or self.quantity < 1:
            raise ValidationError({"quantity": _("La quantité doit être au moins 1.")})

        # produit actif
        if self.product_id and hasattr(self.product, "is_active") and not self.product.is_active:
            raise ValidationError({"product": _("Ce produit n’est pas disponible (inactif).")})

        # stock (si tu veux autoriser stock=0 pour services, ça doit être géré au niveau Product/Category)
        # stock (prod): seulement si track_stock=True
        if self.product_id and hasattr(self.product, "stock"):
            track = getattr(self.product, "track_stock", True)
            if track:
                if self.product.stock is not None and self.product.stock < self.quantity:
                    raise ValidationError({"quantity": _("Stock insuffisant pour la quantité demandée.")})

        # devise : hérite du panier si vide
        if not self.currency and getattr(self.cart, "currency", None):
            self.currency = (self.cart.currency or "").strip().upper()

        if self.currency:
            self.currency = self.currency.strip().upper()

        # si unit_price est 0, on le remplira en save()
        if self.unit_price is None:
            self.unit_price = Decimal("0.00")

    def save(self, *args, **kwargs):
        # auto-remplir le prix à l’ajout/si vide
        if (self.unit_price is None) or (Decimal(self.unit_price) <= Decimal("0")):
            self.unit_price = self._resolve_unit_price()

        # sécurise même hors admin
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self) -> Decimal:
        return (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"))







# # economic/ecommerce/models/cart_item.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from .cart import Cart
# from .product import Product


# class CartItem(models.Model):
#     cart = models.ForeignKey(
#         Cart,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Panier"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="cart_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(
#         default=1,
#         verbose_name=_("Quantité"),
#     )

#     unit_price = models.DecimalField(
#         _("Prix unitaire"),
#         max_digits=10,
#         decimal_places=2,
#         default=0.00,
#     )

#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         verbose_name = _("Article du panier")
#         verbose_name_plural = _("Articles du panier")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["cart", "product"],
#                 name="unique_product_per_cart",
#             )
#         ]

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"

#     @property
#     def total_price(self):
#         return self.unit_price * self.quantity





# # /economic/ecommerce/models/cart_item.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .cart import Cart
# from .product import Product


# class CartItem(models.Model):
#     cart = models.ForeignKey(
#         Cart,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Panier"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="cart_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(
#         default=1,
#         verbose_name=_("Quantité"),
#     )

#     class Meta:
#         verbose_name = _("Article du panier")
#         verbose_name_plural = _("Articles du panier")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["cart", "product"],
#                 name="unique_product_per_cart",
#             )
#         ]

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"
