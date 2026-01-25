# economic/ecommerce/models/product_pricing.py
from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


class PricingType(models.TextChoices):
    B2C = "B2C", _("B2C – Particulier")
    B2B = "B2B", _("B2B – Professionnel")


class ProductPricing(models.Model):
    """
    Prix principal d’un produit.
    - base_price : prix standard
    - promo_price : prix promo optionnel (avec période)
    - bulk_prices : paliers dégressifs (souvent B2B)
    """

    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name="pricing",
        verbose_name=_("Produit"),
    )

    pricing_type = models.CharField(
        max_length=3,
        choices=PricingType.choices,
        default=PricingType.B2C,
        verbose_name=_("Type de tarification"),
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Actif"),
        help_text=_("Désactiver la tarification sans supprimer."),
    )

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name=_("Prix de base"),
    )

    promo_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name=_("Prix promotionnel"),
    )

    promo_start = models.DateTimeField(blank=True, null=True, verbose_name=_("Début promo"))
    promo_end = models.DateTimeField(blank=True, null=True, verbose_name=_("Fin promo"))

    currency = models.CharField(
        max_length=5,
        default="XOF",
        verbose_name=_("Devise"),
        help_text=_("Ex: XOF, EUR, USD"),
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Tarification produit")
        verbose_name_plural = _("Tarifications produits")
        indexes = [
            models.Index(fields=["pricing_type", "currency", "is_active"]),
            models.Index(fields=["promo_start", "promo_end"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} — {self.base_price} {self.currency}"

    # -------------------------
    # Validation / normalisation (prod)
    # -------------------------
    def clean(self):
        super().clean()

        if self.currency:
            self.currency = self.currency.strip().upper()

        if self.base_price is None:
            raise ValidationError({"base_price": _("Le prix de base est obligatoire.")})
        if self.base_price < 0:
            raise ValidationError({"base_price": _("Le prix de base ne peut pas être négatif.")})

        # Promo: cohérence
        if self.promo_price is not None:
            if self.promo_price < 0:
                raise ValidationError({"promo_price": _("Le prix promo ne peut pas être négatif.")})
            if self.promo_price >= self.base_price:
                raise ValidationError({"promo_price": _("Le prix promo doit être inférieur au prix de base.")})

        # Dates promo (si les deux existent)
        if self.promo_start and self.promo_end and self.promo_start > self.promo_end:
            raise ValidationError({"promo_end": _("La fin de promo doit être après le début de promo.")})

        # Si une période promo est définie, il faut un promo_price
        if (self.promo_start or self.promo_end) and self.promo_price is None:
            raise ValidationError({"promo_price": _("Renseignez un prix promo si vous définissez une période promo.")})

    def save(self, *args, **kwargs):
        if self.currency:
            self.currency = self.currency.strip().upper()

        # ✅ sécurité prod : garantit clean() même hors admin
        self.full_clean()
        super().save(*args, **kwargs)

        # ✅ Cohérence prod : éviter deux prix divergents (Product.price vs base_price)
        # On sync sans appeler Product.save() (évite SKU/slug/side-effects).
        try:
            Product = self.product.__class__
            Product.objects.filter(pk=self.product_id).exclude(price=self.base_price).update(price=self.base_price)
        except Exception:
            pass

    # -------------------------
    # Promo helpers
    # -------------------------
    def has_promo(self) -> bool:
        if not self.is_active:
            return False
        if self.promo_price is None:
            return False
        current = now()
        if self.promo_start and current < self.promo_start:
            return False
        if self.promo_end and current > self.promo_end:
            return False
        return True

    @property
    def effective_unit_price(self) -> Decimal:
        return self.promo_price if self.has_promo() else self.base_price

    def get_unit_price(self) -> Decimal:
        return self.effective_unit_price

    def get_bulk_unit_price(self, quantity: int) -> Decimal:
        if not self.is_active:
            return self.base_price
        if not quantity or quantity < 1:
            return self.effective_unit_price
        tier = self.bulk_prices.filter(min_quantity__lte=quantity).order_by("-min_quantity").first()
        return tier.unit_price if tier else self.effective_unit_price

    def effective_total_price(self, quantity: int) -> Decimal:
        qty = int(quantity or 0)
        if qty < 1:
            return Decimal("0")
        return self.get_bulk_unit_price(qty) * Decimal(qty)


class BulkPrice(models.Model):
    """
    Paliers de prix dégressifs.
    """

    pricing = models.ForeignKey(
        ProductPricing,
        on_delete=models.CASCADE,
        related_name="bulk_prices",
        verbose_name=_("Tarification"),
    )

    min_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantité minimale"),
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name=_("Prix unitaire"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        ordering = ["min_quantity"]
        verbose_name = _("Prix dégressif")
        verbose_name_plural = _("Prix dégressifs")
        constraints = [
            models.UniqueConstraint(fields=["pricing", "min_quantity"], name="uniq_bulkprice_pricing_minqty"),
        ]
        indexes = [
            models.Index(fields=["pricing", "min_quantity"]),
        ]

    def __str__(self) -> str:
        return f"{self.pricing.product} — {self.min_quantity}+ → {self.unit_price}"

    def clean(self):
        super().clean()

        if self.pricing_id and self.unit_price is not None:
            if self.unit_price >= self.pricing.base_price:
                raise ValidationError({"unit_price": _("Le prix dégressif doit être inférieur au prix de base.")})

            # cohérence paliers: quantité ↑ => prix doit être <= palier précédent
            lower = (
                BulkPrice.objects.filter(pricing_id=self.pricing_id, min_quantity__lt=self.min_quantity)
                .exclude(pk=self.pk)
                .order_by("-min_quantity")
                .first()
            )
            if lower and self.unit_price > lower.unit_price:
                raise ValidationError({"unit_price": _("Le prix doit être ≤ au palier précédent (quantité plus faible).")})

            higher = (
                BulkPrice.objects.filter(pricing_id=self.pricing_id, min_quantity__gt=self.min_quantity)
                .exclude(pk=self.pk)
                .order_by("min_quantity")
                .first()
            )
            if higher and self.unit_price < higher.unit_price:
                raise ValidationError({"unit_price": _("Le prix doit être ≥ au palier suivant (quantité plus élevée).")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)






# # economic/ecommerce/models/product_pricing.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.timezone import now


# class PricingType(models.TextChoices):
#     B2C = "B2C", _("B2C – Particulier")
#     B2B = "B2B", _("B2B – Professionnel")


# class ProductPricing(models.Model):
#     """
#     Prix principal d’un produit.
#     - base_price : prix standard
#     - promo_price : prix promo optionnel (avec période)
#     - bulk_prices : paliers dégressifs (souvent B2B)
#     """

#     product = models.OneToOneField(
#         "Product",
#         on_delete=models.CASCADE,
#         related_name="pricing",
#         verbose_name=_("Produit"),
#     )

#     pricing_type = models.CharField(
#         max_length=3,
#         choices=PricingType.choices,
#         default=PricingType.B2C,
#         verbose_name=_("Type de tarification"),
#         db_index=True,
#     )

#     # ✅ Activer/désactiver la tarification
#     is_active = models.BooleanField(
#         default=True,
#         db_index=True,
#         verbose_name=_("Actif"),
#         help_text=_("Désactiver la tarification sans supprimer."),
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix de base"),
#     )

#     promo_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix promotionnel"),
#     )

#     promo_start = models.DateTimeField(blank=True, null=True, verbose_name=_("Début promo"))
#     promo_end = models.DateTimeField(blank=True, null=True, verbose_name=_("Fin promo"))

#     currency = models.CharField(
#         max_length=5,
#         default="XOF",
#         verbose_name=_("Devise"),
#         help_text=_("Ex: XOF, EUR, USD"),
#         db_index=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Tarification produit")
#         verbose_name_plural = _("Tarifications produits")
#         indexes = [
#             models.Index(fields=["pricing_type", "currency", "is_active"]),
#             models.Index(fields=["promo_start", "promo_end"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.product} — {self.base_price} {self.currency}"

#     def clean(self):
#         super().clean()

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         if self.base_price is None:
#             raise ValidationError({"base_price": _("Le prix de base est obligatoire.")})

#         if self.base_price is not None and self.base_price < 0:
#             raise ValidationError({"base_price": _("Le prix de base ne peut pas être négatif.")})

#         # Promo: cohérence
#         if self.promo_price is not None:
#             if self.promo_price >= self.base_price:
#                 raise ValidationError({"promo_price": _("Le prix promo doit être inférieur au prix de base.")})

#         # Dates promo
#         if self.promo_start and self.promo_end and self.promo_start > self.promo_end:
#             raise ValidationError({"promo_end": _("La fin de promo doit être après le début de promo.")})

#         if (self.promo_start or self.promo_end) and self.promo_price is None:
#             raise ValidationError({"promo_price": _("Renseignez un prix promo si vous définissez une période promo.")})

#         # Si inactif: pas d'obligation, mais utile d'éviter des incohérences côté code
#         if not self.is_active and self.promo_price is not None:
#             # pas une erreur bloquante; tu peux garder, mais on peut aussi forcer.
#             pass

#     def save(self, *args, **kwargs):
#         if self.currency:
#             self.currency = self.currency.strip().upper()
#         super().save(*args, **kwargs)

#     def has_promo(self) -> bool:
#         if not self.is_active:
#             return False
#         if self.promo_price is None:
#             return False
#         current = now()
#         if self.promo_start and current < self.promo_start:
#             return False
#         if self.promo_end and current > self.promo_end:
#             return False
#         return True

#     @property
#     def effective_unit_price(self) -> Decimal:
#         return self.promo_price if self.has_promo() else self.base_price

#     def get_unit_price(self) -> Decimal:
#         return self.effective_unit_price

#     def get_bulk_unit_price(self, quantity: int) -> Decimal:
#         if not self.is_active:
#             return self.base_price
#         if not quantity or quantity < 1:
#             return self.effective_unit_price
#         tier = self.bulk_prices.filter(min_quantity__lte=quantity).order_by("-min_quantity").first()
#         return tier.unit_price if tier else self.effective_unit_price

#     def effective_total_price(self, quantity: int) -> Decimal:
#         qty = int(quantity or 0)
#         if qty < 1:
#             return Decimal("0")
#         return self.get_bulk_unit_price(qty) * Decimal(qty)


# class BulkPrice(models.Model):
#     """
#     Paliers de prix dégressifs.
#     """

#     pricing = models.ForeignKey(
#         ProductPricing,
#         on_delete=models.CASCADE,
#         related_name="bulk_prices",
#         verbose_name=_("Tarification"),
#     )

#     min_quantity = models.PositiveIntegerField(
#         validators=[MinValueValidator(1)],
#         verbose_name=_("Quantité minimale"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix unitaire"),
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         ordering = ["min_quantity"]
#         verbose_name = _("Prix dégressif")
#         verbose_name_plural = _("Prix dégressifs")
#         constraints = [
#             models.UniqueConstraint(fields=["pricing", "min_quantity"], name="uniq_bulkprice_pricing_minqty"),
#         ]
#         indexes = [
#             models.Index(fields=["pricing", "min_quantity"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.pricing.product} — {self.min_quantity}+ → {self.unit_price}"

#     def clean(self):
#         super().clean()

#         if self.pricing_id and self.unit_price is not None:
#             # règle simple : le palier doit être < base_price
#             if self.unit_price >= self.pricing.base_price:
#                 raise ValidationError({"unit_price": _("Le prix dégressif doit être inférieur au prix de base.")})

#             # ✅ cohérence des paliers (prod):
#             # - plus la quantité mini est grande, plus le prix unitaire doit être <= palier précédent
#             lower = (
#                 BulkPrice.objects.filter(pricing_id=self.pricing_id, min_quantity__lt=self.min_quantity)
#                 .exclude(pk=self.pk)
#                 .order_by("-min_quantity")
#                 .first()
#             )
#             if lower and self.unit_price > lower.unit_price:
#                 raise ValidationError(
#                     {"unit_price": _("Le prix doit être ≤ au palier précédent (quantité plus faible).")}
#                 )

#             higher = (
#                 BulkPrice.objects.filter(pricing_id=self.pricing_id, min_quantity__gt=self.min_quantity)
#                 .exclude(pk=self.pk)
#                 .order_by("min_quantity")
#                 .first()
#             )
#             if higher and self.unit_price < higher.unit_price:
#                 raise ValidationError(
#                     {"unit_price": _("Le prix doit être ≥ au palier suivant (quantité plus élevée).")}
#                 )




# # economic/ecommerce/models/product_pricing.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.timezone import now


# class PricingType(models.TextChoices):
#     B2C = "B2C", _("B2C – Particulier")
#     B2B = "B2B", _("B2B – Professionnel")


# class ProductPricing(models.Model):
#     """
#     Prix principal d’un produit.
#     - base_price : prix standard
#     - promo_price : prix promo optionnel (avec période)
#     - bulk_prices : paliers dégressifs (souvent B2B)
#     """

#     product = models.OneToOneField(
#         "Product",
#         on_delete=models.CASCADE,
#         related_name="pricing",
#         verbose_name=_("Produit"),
#     )

#     pricing_type = models.CharField(
#         max_length=3,
#         choices=PricingType.choices,
#         default=PricingType.B2C,
#         verbose_name=_("Type de tarification"),
#         db_index=True,
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix de base"),
#     )

#     promo_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix promotionnel"),
#     )

#     promo_start = models.DateTimeField(blank=True, null=True, verbose_name=_("Début promo"))
#     promo_end = models.DateTimeField(blank=True, null=True, verbose_name=_("Fin promo"))

#     currency = models.CharField(
#         max_length=5,
#         default="XOF",
#         verbose_name=_("Devise"),
#         help_text=_("Ex: XOF, EUR, USD"),
#         db_index=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Tarification produit")
#         verbose_name_plural = _("Tarifications produits")
#         indexes = [
#             models.Index(fields=["pricing_type", "currency"]),
#             models.Index(fields=["promo_start", "promo_end"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.product} — {self.base_price} {self.currency}"

#     def clean(self):
#         super().clean()

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         if self.base_price is None:
#             raise ValidationError({"base_price": _("Le prix de base est obligatoire.")})

#         # Promo: cohérence
#         if self.promo_price is not None:
#             if self.promo_price >= self.base_price:
#                 raise ValidationError({"promo_price": _("Le prix promo doit être inférieur au prix de base.")})

#         # Dates promo
#         if self.promo_start and self.promo_end and self.promo_start > self.promo_end:
#             raise ValidationError({"promo_end": _("La fin de promo doit être après le début de promo.")})

#         if (self.promo_start or self.promo_end) and self.promo_price is None:
#             raise ValidationError({"promo_price": _("Renseignez un prix promo si vous définissez une période promo.")})

#     def has_promo(self) -> bool:
#         if self.promo_price is None:
#             return False
#         current = now()
#         if self.promo_start and current < self.promo_start:
#             return False
#         if self.promo_end and current > self.promo_end:
#             return False
#         return True

#     @property
#     def effective_unit_price(self) -> Decimal:
#         return self.promo_price if self.has_promo() else self.base_price

#     def get_unit_price(self) -> Decimal:
#         return self.effective_unit_price

#     def get_bulk_unit_price(self, quantity: int) -> Decimal:
#         if not quantity or quantity < 1:
#             return self.effective_unit_price
#         tier = self.bulk_prices.filter(min_quantity__lte=quantity).order_by("-min_quantity").first()
#         return tier.unit_price if tier else self.effective_unit_price


# class BulkPrice(models.Model):
#     """
#     Paliers de prix dégressifs.
#     """

#     pricing = models.ForeignKey(
#         ProductPricing,
#         on_delete=models.CASCADE,
#         related_name="bulk_prices",
#         verbose_name=_("Tarification"),
#     )

#     min_quantity = models.PositiveIntegerField(
#         validators=[MinValueValidator(1)],
#         verbose_name=_("Quantité minimale"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix unitaire"),
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))

#     class Meta:
#         ordering = ["min_quantity"]
#         verbose_name = _("Prix dégressif")
#         verbose_name_plural = _("Prix dégressifs")
#         constraints = [
#             models.UniqueConstraint(fields=["pricing", "min_quantity"], name="uniq_bulkprice_pricing_minqty"),
#         ]
#         indexes = [
#             models.Index(fields=["pricing", "min_quantity"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.pricing.product} — {self.min_quantity}+ → {self.unit_price}"

#     def clean(self):
#         super().clean()
#         if self.pricing_id and self.unit_price is not None:
#             # On garde une règle simple : le palier doit être < base_price
#             if self.unit_price >= self.pricing.base_price:
#                 raise ValidationError({"unit_price": _("Le prix dégressif doit être inférieur au prix de base.")})





# # economic/ecommerce/models/product_pricing.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.timezone import now


# class PricingType(models.TextChoices):
#     B2C = "B2C", _("B2C – Particulier")
#     B2B = "B2B", _("B2B – Professionnel")


# class ProductPricing(models.Model):
#     """
#     Prix principal d’un produit (B2C et/ou B2B).
#     - `base_price` : prix standard
#     - `promo_price` : prix promo optionnel (avec fenêtre promo)
#     - `bulk_prices` : paliers de prix dégressifs (souvent B2B)
#     """

#     product = models.OneToOneField(
#         "Product",  # ✅ robuste (évite les soucis de label app)
#         on_delete=models.CASCADE,
#         related_name="pricing",
#         verbose_name=_("Produit"),
#     )

#     pricing_type = models.CharField(
#         max_length=3,
#         choices=PricingType.choices,
#         default=PricingType.B2C,
#         verbose_name=_("Type de tarification"),
#         db_index=True,
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix de base"),
#     )

#     promo_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix promotionnel"),
#     )

#     promo_start = models.DateTimeField(blank=True, null=True, verbose_name=_("Début promo"))
#     promo_end = models.DateTimeField(blank=True, null=True, verbose_name=_("Fin promo"))

#     currency = models.CharField(
#         max_length=5,
#         default="XOF",
#         verbose_name=_("Devise"),
#         help_text=_("Ex: XOF, EUR, USD"),
#         db_index=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Tarification produit")
#         verbose_name_plural = _("Tarifications produits")
#         indexes = [
#             models.Index(fields=["pricing_type", "currency"]),
#             models.Index(fields=["promo_start", "promo_end"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.product} — {self.base_price} {self.currency}"

#     # -------------------------
#     # Validation prod
#     # -------------------------
#     def clean(self):
#         super().clean()

#         # Normalise devise
#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         # Promo coherente
#         if self.promo_price is not None:
#             if self.promo_price >= self.base_price:
#                 raise ValidationError(
#                     {"promo_price": _("Le prix promo doit être inférieur au prix de base.")}
#                 )

#         # Dates promo
#         if self.promo_start and self.promo_end and self.promo_start > self.promo_end:
#             raise ValidationError({"promo_end": _("La fin de promo doit être après le début de promo.")})

#         # Si promo_start/end est défini mais pas promo_price -> incohérence (optionnel, mais recommandé)
#         if (self.promo_start or self.promo_end) and self.promo_price is None:
#             raise ValidationError({"promo_price": _("Renseignez un prix promo si vous définissez une période promo.")})

#     def has_promo(self) -> bool:
#         """
#         Retourne True si une promo est active maintenant.
#         """
#         if self.promo_price is None:
#             return False

#         current = now()
#         if self.promo_start and current < self.promo_start:
#             return False
#         if self.promo_end and current > self.promo_end:
#             return False
#         return True

#     @property
#     def effective_unit_price(self) -> Decimal:
#         """
#         Prix unitaire effectif (sans volume).
#         """
#         return self.promo_price if self.has_promo() else self.base_price

#     def get_unit_price(self) -> Decimal:
#         """
#         Compat (si tu l’utilises déjà dans templates/services).
#         """
#         return self.effective_unit_price

#     def get_bulk_unit_price(self, quantity: int) -> Decimal:
#         """
#         Retourne le meilleur prix unitaire selon quantité (paliers).
#         Si aucun palier applicable, retourne effective_unit_price.
#         """
#         if not quantity or quantity < 1:
#             return self.effective_unit_price

#         qs = self.bulk_prices.filter(min_quantity__lte=quantity).order_by("-min_quantity")
#         tier = qs.first()
#         return tier.unit_price if tier else self.effective_unit_price


# class BulkPrice(models.Model):
#     """
#     Prix dégressifs (paliers), généralement pour B2B.
#     """

#     pricing = models.ForeignKey(
#         ProductPricing,
#         on_delete=models.CASCADE,
#         related_name="bulk_prices",
#         verbose_name=_("Tarification"),
#     )

#     min_quantity = models.PositiveIntegerField(
#         validators=[MinValueValidator(1)],
#         verbose_name=_("Quantité minimale"),
#     )

#     unit_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal("0"))],
#         verbose_name=_("Prix unitaire"),
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))

#     class Meta:
#         ordering = ["min_quantity"]
#         verbose_name = _("Prix dégressif")
#         verbose_name_plural = _("Prix dégressifs")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["pricing", "min_quantity"],
#                 name="uniq_bulkprice_pricing_minqty",
#             )
#         ]
#         indexes = [
#             models.Index(fields=["pricing", "min_quantity"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.min_quantity}+ → {self.unit_price}"

#     def clean(self):
#         super().clean()

#         # Prix palier doit être <= prix effectif (sinon palier inutile/illogique)
#         # (Tu peux assouplir si tu veux autoriser paliers > base_price.)
#         if self.pricing_id and self.unit_price is not None:
#             base = self.pricing.base_price
#             if self.unit_price >= base:
#                 raise ValidationError({"unit_price": _("Le prix dégressif doit être inférieur au prix de base.")})






# # economic/ecommerce/models/product_pricing.py
# from django.db import models
# from django.core.validators import MinValueValidator
# from django.utils.translation import gettext_lazy as _


# class PricingType(models.TextChoices):
#     B2C = "B2C", _("B2C – Particulier")
#     B2B = "B2B", _("B2B – Professionnel")


# class ProductPricing(models.Model):
#     """
#     Prix principal d’un produit (B2C et/ou B2B)
#     """
#     product = models.OneToOneField(
#         "ecommerce.Product",
#         on_delete=models.CASCADE,
#         related_name="pricing"
#     )

#     pricing_type = models.CharField(
#         max_length=3,
#         choices=PricingType.choices,
#         default=PricingType.B2C
#     )

#     # Prix standard (B2C ou base B2B)
#     base_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(0)],
#         verbose_name=_("Prix de base")
#     )

#     # Promotion
#     promo_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(0)],
#         verbose_name=_("Prix promotionnel")
#     )

#     promo_start = models.DateTimeField(blank=True, null=True)
#     promo_end = models.DateTimeField(blank=True, null=True)

#     currency = models.CharField(
#         max_length=5,
#         default="EUR",
#         verbose_name=_("Devise")
#     )

#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Tarification produit")
#         verbose_name_plural = _("Tarifications produits")

#     def __str__(self):
#         return f"{self.product} – {self.base_price} {self.currency}"

#     def has_promo(self):
#         if not self.promo_price:
#             return False
#         from django.utils.timezone import now
#         current = now()
#         if self.promo_start and current < self.promo_start:
#             return False
#         if self.promo_end and current > self.promo_end:
#             return False
#         return True

#     def get_unit_price(self):
#         """
#         Prix unitaire effectif (sans tenir compte des volumes)
#         """
#         if self.has_promo():
#             return self.promo_price
#         return self.base_price

# class BulkPrice(models.Model):
#     """
#     Prix dégressifs B2B (MOQ inclus)
#     """
#     pricing = models.ForeignKey(
#         ProductPricing,
#         on_delete=models.CASCADE,
#         related_name="bulk_prices"
#     )

#     min_quantity = models.PositiveIntegerField(
#         validators=[MinValueValidator(1)],
#         verbose_name=_("Quantité minimale")
#     )

#     unit_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(0)],
#         verbose_name=_("Prix unitaire")
#     )

#     class Meta:
#         ordering = ["min_quantity"]
#         verbose_name = _("Prix dégressif")
#         verbose_name_plural = _("Prix dégressifs")

#     def __str__(self):
#         return f"{self.min_quantity}+ → {self.unit_price}"
