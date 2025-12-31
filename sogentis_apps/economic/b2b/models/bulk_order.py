# /economic/b2b/models/bulk_order.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from economic.b2b.models.company import Company


class BulkOrder(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Brouillon")),
        ("submitted", _("Soumise")),
        ("approved", _("Approuvée")),
        ("rejected", _("Rejetée")),
        ("invoiced", _("Facturée")),
        ("paid", _("Payée")),
        ("cancelled", _("Annulée")),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="bulk_orders",
        verbose_name=_("Entreprise"),
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Référence interne"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Statut"),
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name=_("Montant total"),
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Commande en gros")
        verbose_name_plural = _("Commandes en gros")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} — {self.uuid}"
