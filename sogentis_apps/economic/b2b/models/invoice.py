# economic/b2b/models/invoice.py
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        ISSUED = "issued", _("Émise")
        PAID = "paid", _("Payée")
        CANCELLED = "cancelled", _("Annulée")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    bulk_order = models.OneToOneField(
        "b2b.BulkOrder",
        on_delete=models.CASCADE,
        related_name="invoice",
        verbose_name=_("Commande en gros"),
    )

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_("Numéro de facture"))

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Statut"),
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Montant"),
    )

    issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date d’émission"))
    due_date = models.DateField(null=True, blank=True, verbose_name=_("Date d’échéance"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de paiement"))

    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["invoice_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_number} — {self.bulk_order.company}"

    def sync_amount_from_order(self, save: bool = True):
        self.amount = self.bulk_order.total_amount
        if save:
            self.save(update_fields=["amount", "updated_at"])
        return self.amount

    def mark_issued(self):
        self.status = self.Status.ISSUED
        self.issued_at = self.issued_at or timezone.now()
        self.amount = self.bulk_order.total_amount
        self.save(update_fields=["status", "issued_at", "amount", "updated_at"])

    def mark_paid(self):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])





# # economic/b2b/models/inoice.py
# import uuid
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models.bulk_order import BulkOrder


# class Invoice(models.Model):
#     STATUS_CHOICES = [
#         ("draft", _("Brouillon")),
#         ("issued", _("Émise")),
#         ("paid", _("Payée")),
#         ("cancelled", _("Annulée")),
#     ]

#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     bulk_order = models.OneToOneField(
#         BulkOrder,
#         on_delete=models.CASCADE,
#         related_name="invoice",
#         verbose_name=_("Commande en gros"),
#     )

#     invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_("Numéro de facture"))

#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name=_("Statut"))

#     amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("Montant"))

#     issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date d’émission"))
#     due_date = models.DateField(null=True, blank=True, verbose_name=_("Date d’échéance"))
#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de paiement"))

#     notes = models.TextField(blank=True, verbose_name=_("Notes"))

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Facture")
#         verbose_name_plural = _("Factures")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.invoice_number} — {self.bulk_order.company}"

#     def mark_issued(self):
#         self.status = "issued"
#         self.issued_at = self.issued_at or timezone.now()
#         # ✅ sync
#         self.amount = self.bulk_order.total_amount
#         self.save(update_fields=["status", "issued_at", "amount"])

#     def mark_paid(self):
#         self.status = "paid"
#         self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at"])






# # economic/b2b/models/invoice.py

# import uuid
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models.bulk_order import BulkOrder


# class Invoice(models.Model):
#     STATUS_CHOICES = [
#         ("draft", _("Brouillon")),
#         ("issued", _("Émise")),
#         ("paid", _("Payée")),
#         ("cancelled", _("Annulée")),
#     ]

#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#     )

#     bulk_order = models.OneToOneField(
#         BulkOrder,
#         on_delete=models.CASCADE,
#         related_name="invoice",
#         verbose_name=_("Commande en gros"),
#     )

#     invoice_number = models.CharField(
#         max_length=50,
#         unique=True,
#         verbose_name=_("Numéro de facture"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="draft",
#         verbose_name=_("Statut"),
#     )

#     amount = models.DecimalField(
#         max_digits=14,
#         decimal_places=2,
#         verbose_name=_("Montant"),
#     )

#     issued_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Date d’émission"),
#     )

#     due_date = models.DateField(
#         null=True,
#         blank=True,
#         verbose_name=_("Date d’échéance"),
#     )

#     paid_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Date de paiement"),
#     )

#     notes = models.TextField(
#         blank=True,
#         verbose_name=_("Notes"),
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Facture")
#         verbose_name_plural = _("Factures")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.invoice_number} — {self.bulk_order.company}"

#     def mark_issued(self):
#         self.status = "issued"
#         self.issued_at = self.issued_at or timezone.now()
#         # sync amount
#         self.amount = self.bulk_order.total_amount
#         self.save(update_fields=["status", "issued_at", "amount"])


#     def mark_paid(self):
#         self.status = "paid"
#         self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at"])
