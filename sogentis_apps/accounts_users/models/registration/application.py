from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class RegistrationCategory(models.TextChoices):
    SOCIAL = "SOCIAL", _("Social")
    ECONOMIC_CLIENT = "ECON_CLIENT", _("Client (B2C)")
    ECONOMIC_VENDOR = "ECON_VENDOR", _("Vendeur")
    ECONOMIC_B2B = "ECON_B2B", _("Entreprise (B2B)")


class RegistrationStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Brouillon")
    PENDING = "PENDING", _("En attente")
    APPROVED = "APPROVED", _("Approuvé")
    REJECTED = "REJECTED", _("Refusé")


class RegistrationApplication(models.Model):
    """
    Dossier d'inscription (KYC / pièces jointes / infos par catégorie).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registration_applications",
        null=True,
        blank=True,
    )

    category = models.CharField(max_length=20, choices=RegistrationCategory.choices)
    status = models.CharField(max_length=20, choices=RegistrationStatus.choices, default=RegistrationStatus.PENDING)

    # Track: client/vendor/b2b (utile côté économique)
    track = models.CharField(max_length=20, blank=True, default="")

    # Infos spécifiques (identification, entreprise, vendeur, etc.)
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.category} / {self.status} / user={self.user_id or '—'}"
