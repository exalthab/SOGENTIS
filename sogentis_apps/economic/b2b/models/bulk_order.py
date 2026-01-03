# economic/b2b/models/bulk_order.py
import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _


class BulkOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        SUBMITTED = "submitted", _("Soumise")
        APPROVED = "approved", _("Approuvée")
        REJECTED = "rejected", _("Rejetée")
        INVOICED = "invoiced", _("Facturée")
        PAID = "paid", _("Payée")
        CANCELLED = "cancelled", _("Annulée")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    company = models.ForeignKey(
        "b2b.Company",
        on_delete=models.CASCADE,
        related_name="bulk_orders",
        verbose_name=_("Entreprise"),
    )

    reference = models.CharField(max_length=100, blank=True, verbose_name=_("Référence interne"))

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Statut"),
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Montant total"),
    )

    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Commande en gros")
        verbose_name_plural = _("Commandes en gros")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.company} — {self.uuid}"

    def recalc_total(self, save: bool = True) -> Decimal:
        total = self.items.aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
        self.total_amount = total
        if save:
            self.save(update_fields=["total_amount", "updated_at"])
        return total





# # economic/b2b/models/bulk_order.py
# import uuid
# from decimal import Decimal
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models.company import Company


# class BulkOrder(models.Model):
#     STATUS_CHOICES = [
#         ("draft", _("Brouillon")),
#         ("submitted", _("Soumise")),
#         ("approved", _("Approuvée")),
#         ("rejected", _("Rejetée")),
#         ("invoiced", _("Facturée")),
#         ("paid", _("Payée")),
#         ("cancelled", _("Annulée")),
#     ]

#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name="bulk_orders",
#         verbose_name=_("Entreprise"),
#     )

#     reference = models.CharField(max_length=100, blank=True, verbose_name=_("Référence interne"))

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="draft",
#         verbose_name=_("Statut"),
#     )

#     total_amount = models.DecimalField(
#         max_digits=14,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Montant total"),
#     )

#     notes = models.TextField(blank=True, verbose_name=_("Notes"))

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Commande en gros")
#         verbose_name_plural = _("Commandes en gros")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.company} — {self.uuid}"

#     def recalc_total(self, save: bool = True):
#         total = Decimal("0.00")
#         for item in self.items.all():
#             total += (item.total_price or Decimal("0.00"))
#         self.total_amount = total
#         if save:
#             self.save(update_fields=["total_amount", "updated_at"])
#         return total





# # /economic/b2b/models/bulk_order.py

# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models.company import Company


# class BulkOrder(models.Model):
#     STATUS_CHOICES = [
#         ("draft", _("Brouillon")),
#         ("submitted", _("Soumise")),
#         ("approved", _("Approuvée")),
#         ("rejected", _("Rejetée")),
#         ("invoiced", _("Facturée")),
#         ("paid", _("Payée")),
#         ("cancelled", _("Annulée")),
#     ]

#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name="bulk_orders",
#         verbose_name=_("Entreprise"),
#     )

#     reference = models.CharField(
#         max_length=100,
#         blank=True,
#         verbose_name=_("Référence interne"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="draft",
#         verbose_name=_("Statut"),
#     )

#     total_amount = models.DecimalField(
#         max_digits=14,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Montant total"),
#     )

#     notes = models.TextField(
#         blank=True,
#         verbose_name=_("Notes"),
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Commande en gros")
#         verbose_name_plural = _("Commandes en gros")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.company} — {self.uuid}"
