# economic/b2b/models/invoice.py

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from economic.b2b.models.bulk_order import BulkOrder


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Brouillon")),
        ("issued", _("Émise")),
        ("paid", _("Payée")),
        ("cancelled", _("Annulée")),
    ]

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    bulk_order = models.OneToOneField(
        BulkOrder,
        on_delete=models.CASCADE,
        related_name="invoice",
        verbose_name=_("Commande en gros"),
    )

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Numéro de facture"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Statut"),
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("Montant"),
    )

    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date d’émission"),
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date d’échéance"),
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de paiement"),
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice_number} — {self.bulk_order.company}"

    def mark_issued(self):
        self.status = "issued"
        self.issued_at = self.issued_at or timezone.now()
        self.save(update_fields=["status", "issued_at"])

    def mark_paid(self):
        self.status = "paid"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])
