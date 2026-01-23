from __future__ import annotations

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .application import RegistrationApplication


def _reg_doc_path(instance: "RegistrationDocument", filename: str) -> str:
    return f"registrations/{instance.application_id}/{uuid.uuid4().hex}_{filename}"


class RegistrationDocType(models.TextChoices):
    ID_FRONT = "ID_FRONT", _("Pièce d'identité (recto)")
    ID_BACK = "ID_BACK", _("Pièce d'identité (verso)")
    SELFIE = "SELFIE", _("Selfie / photo")

    PROOF_ADDRESS = "PROOF_ADDRESS", _("Justificatif de domicile")

    BUSINESS_LICENSE = "BUSINESS_LICENSE", _("Autorisation / Registre commerce")
    TAX_CERTIFICATE = "TAX_CERTIFICATE", _("Attestation fiscale")
    BANK_RIB = "BANK_RIB", _("RIB / Compte bancaire")

    RCCM = "RCCM", _("RCCM / Registre")
    NINEA = "NINEA", _("NINEA / Identifiant")
    COMPANY_STATUTES = "COMPANY_STATUTES", _("Statuts")
    OTHER = "OTHER", _("Autre")


class RegistrationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    application = models.ForeignKey(
        RegistrationApplication,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    doc_type = models.CharField(max_length=30, choices=RegistrationDocType.choices)
    file = models.FileField(upload_to=_reg_doc_path)
    note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.doc_type} / {self.application_id}"
