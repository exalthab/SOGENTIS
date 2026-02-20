# economic/prestations/models/offers.py
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryMode(models.TextChoices):
    SERVICE = "SERVICE", _("Service (réalisation)")
    DOWNLOAD = "DOWNLOAD", _("Digital (fichier à télécharger)")
    LINK = "LINK", _("Digital (lien privé)")


class BaseOffer(models.Model):
    """
    Variante/Option tarifée (ou sur devis) — style "Infomaniak":
    - Landing Page / Pro / Premium, etc.
    - Preview (URL) possible
    - Livraison: service / download / lien
    """

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=220)
    subtitle = models.CharField(max_length=255, blank=True)
    short_description = models.CharField(max_length=320, blank=True)
    description = models.TextField(blank=True)

    # Prix nullable => "Sur devis"
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="XOF")

    allow_online_payment = models.BooleanField(default=False)
    delivery_mode = models.CharField(max_length=16, choices=DeliveryMode.choices, default=DeliveryMode.SERVICE)

    # Preview / demo
    preview_url = models.URLField(blank=True)
    preview_label = models.CharField(max_length=64, blank=True, default="Preview")

    # Livrables digitaux (optionnels)
    deliverable_file = models.FileField(upload_to="prestations/deliverables/%Y/%m/", blank=True)
    deliverable_url = models.URLField(blank=True)
    deliverable_notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-is_featured", "order", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["is_active", "is_featured", "order"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.title or self.slug

    @property
    def is_quote_only(self) -> bool:
        return self.price is None

    def clean(self):
        # si digital => au moins un livrable (file/url) recommandé (pas forcé pour éviter de casser)
        super().clean()


class PrestationPlan(BaseOffer):
    prestation = models.ForeignKey(
        "prestations.Prestation",
        on_delete=models.CASCADE,
        related_name="plans",
    )

    class Meta(BaseOffer.Meta):
        constraints = [
            models.UniqueConstraint(fields=["prestation", "slug"], name="uniq_prestation_plan_slug"),
        ]
        indexes = BaseOffer.Meta.indexes + [
            models.Index(fields=["prestation", "is_active", "order"]),
        ]


class PackageOffer(BaseOffer):
    package = models.ForeignKey(
        "prestations.PrestationPackage",
        on_delete=models.CASCADE,
        related_name="offers",
    )

    class Meta(BaseOffer.Meta):
        constraints = [
            models.UniqueConstraint(fields=["package", "slug"], name="uniq_package_offer_slug"),
        ]
        indexes = BaseOffer.Meta.indexes + [
            models.Index(fields=["package", "is_active", "order"]),
        ]
