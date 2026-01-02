from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .company import Company


class RFQ(models.Model):
    class RFQStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Brouillon")
        OPEN = "OPEN", _("Ouvert")
        CLOSED = "CLOSED", _("Fermé")
        CANCELLED = "CANCELLED", _("Annulé")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="b2b_rfqs",
        verbose_name=_("Créé par"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="rfqs",
        verbose_name=_("Entreprise"),
    )

    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    quantity = models.DecimalField(_("Quantité"), max_digits=12, decimal_places=2, default=1)
    unit = models.CharField(_("Unité"), max_length=30, blank=True)  # ex: kg, piece, mois

    budget_min = models.DecimalField(_("Budget min"), max_digits=14, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(_("Budget max"), max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(_("Devise"), max_length=10, default="XOF")

    deadline = models.DateField(_("Date limite"), null=True, blank=True)

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=RFQStatus.choices,
        default=RFQStatus.DRAFT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Demande de devis (RFQ)")
        verbose_name_plural = _("Demandes de devis (RFQ)")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["status"]),
            models.Index(fields=["deadline"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return self.title
