from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .rfq import RFQ


class Offer(models.Model):
    class OfferStatus(models.TextChoices):
        SUBMITTED = "SUBMITTED", _("Soumise")
        SHORTLISTED = "SHORTLISTED", _("Pré-sélectionnée")
        ACCEPTED = "ACCEPTED", _("Acceptée")
        REJECTED = "REJECTED", _("Rejetée")
        WITHDRAWN = "WITHDRAWN", _("Retirée")

    rfq = models.ForeignKey(
        RFQ,
        on_delete=models.CASCADE,
        related_name="offers",
        verbose_name=_("RFQ"),
    )

    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="b2b_offers",
        verbose_name=_("Fournisseur"),
    )

    message = models.TextField(_("Message"), blank=True)
    price_total = models.DecimalField(_("Prix total"), max_digits=14, decimal_places=2)
    currency = models.CharField(_("Devise"), max_length=10, default="XOF")

    delivery_days = models.PositiveIntegerField(_("Délai (jours)"), default=7)
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=OfferStatus.choices,
        default=OfferStatus.SUBMITTED,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Offre")
        verbose_name_plural = _("Offres")
        ordering = ("-created_at",)
        unique_together = (("rfq", "supplier"),)
        indexes = [
            models.Index(fields=["rfq"]),
            models.Index(fields=["supplier"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.rfq} — {self.supplier}"
