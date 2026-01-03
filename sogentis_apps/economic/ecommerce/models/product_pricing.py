from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class PricingType(models.TextChoices):
    B2C = "B2C", _("B2C – Particulier")
    B2B = "B2B", _("B2B – Professionnel")


class ProductPricing(models.Model):
    """
    Prix principal d’un produit (B2C et/ou B2B)
    """
    product = models.OneToOneField(
        "ecommerce.Product",
        on_delete=models.CASCADE,
        related_name="pricing"
    )

    pricing_type = models.CharField(
        max_length=3,
        choices=PricingType.choices,
        default=PricingType.B2C
    )

    # Prix standard (B2C ou base B2B)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Prix de base")
    )

    # Promotion
    promo_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Prix promotionnel")
    )

    promo_start = models.DateTimeField(blank=True, null=True)
    promo_end = models.DateTimeField(blank=True, null=True)

    currency = models.CharField(
        max_length=5,
        default="EUR",
        verbose_name=_("Devise")
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Tarification produit")
        verbose_name_plural = _("Tarifications produits")

    def __str__(self):
        return f"{self.product} – {self.base_price} {self.currency}"

    def has_promo(self):
        if not self.promo_price:
            return False
        from django.utils.timezone import now
        current = now()
        if self.promo_start and current < self.promo_start:
            return False
        if self.promo_end and current > self.promo_end:
            return False
        return True

    def get_unit_price(self):
        """
        Prix unitaire effectif (sans tenir compte des volumes)
        """
        if self.has_promo():
            return self.promo_price
        return self.base_price

class BulkPrice(models.Model):
    """
    Prix dégressifs B2B (MOQ inclus)
    """
    pricing = models.ForeignKey(
        ProductPricing,
        on_delete=models.CASCADE,
        related_name="bulk_prices"
    )

    min_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantité minimale")
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Prix unitaire")
    )

    class Meta:
        ordering = ["min_quantity"]
        verbose_name = _("Prix dégressif")
        verbose_name_plural = _("Prix dégressifs")

    def __str__(self):
        return f"{self.min_quantity}+ → {self.unit_price}"
