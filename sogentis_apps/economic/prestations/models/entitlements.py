# economic/prestations/models/entitlements.py
from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EntitlementStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Actif")
    REVOKED = "REVOKED", _("Révoqué")
    EXPIRED = "EXPIRED", _("Expiré")


class PaymentProvider(models.TextChoices):
    STRIPE = "STRIPE", "Stripe"
    PAYPAL = "PAYPAL", "PayPal"
    WAVE = "WAVE", "Wave"
    ORANGE = "ORANGE", "Orange Money"
    MANUAL = "MANUAL", _("Manuel")


class PrestationEntitlement(models.Model):
    """
    Donne accès (après paiement) à un livrable digital ou à une option/prestation.
    XOR strict: un seul des 4 champs de cible doit être rempli.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prestations_entitlements")

    prestation_plan = models.ForeignKey(
        "prestations.PrestationPlan",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="entitlements",
    )
    package_offer = models.ForeignKey(
        "prestations.PackageOffer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="entitlements",
    )
    prestation = models.ForeignKey(
        "prestations.Prestation",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="entitlements",
    )
    package = models.ForeignKey(
        "prestations.PrestationPackage",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="entitlements",
    )

    status = models.CharField(max_length=10, choices=EntitlementStatus.choices, default=EntitlementStatus.ACTIVE)

    provider = models.CharField(max_length=16, choices=PaymentProvider.choices, blank=True)
    provider_ref = models.CharField(max_length=128, blank=True)
    order_reference = models.CharField(max_length=64, blank=True)

    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    paid_currency = models.CharField(max_length=8, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    download_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    download_limit = models.PositiveSmallIntegerField(default=5)
    download_count = models.PositiveSmallIntegerField(default=0)

    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["user", "status", "-created_at"]),
            models.Index(fields=["download_token"]),
        ]
        constraints = [
            # EXACTEMENT 1 cible remplie
            models.CheckConstraint(
                name="ck_entitlement_exactly_one_target",
                check=(
                    Q(prestation_plan__isnull=False, package_offer__isnull=True, prestation__isnull=True, package__isnull=True)
                    | Q(prestation_plan__isnull=True, package_offer__isnull=False, prestation__isnull=True, package__isnull=True)
                    | Q(prestation_plan__isnull=True, package_offer__isnull=True, prestation__isnull=False, package__isnull=True)
                    | Q(prestation_plan__isnull=True, package_offer__isnull=True, prestation__isnull=True, package__isnull=False)
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"Entitlement #{self.id} ({self.user_id})"

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and timezone.now() >= self.expires_at)

    def can_download(self) -> bool:
        if self.status != EntitlementStatus.ACTIVE:
            return False
        if self.is_expired:
            return False
        return self.download_count < self.download_limit

    def mark_download(self) -> None:
        if self.download_count < 65535:
            self.download_count += 1
            self.save(update_fields=["download_count", "updated_at"])

    @property
    def deliverable_file(self):
        obj = self.prestation_plan or self.package_offer
        return getattr(obj, "deliverable_file", None) if obj else None

    @property
    def deliverable_url(self) -> str:
        obj = self.prestation_plan or self.package_offer
        return (getattr(obj, "deliverable_url", "") or "") if obj else ""
