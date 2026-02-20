# accounting/models/journal_entry.py
from __future__ import annotations

import uuid as uuidlib
from decimal import Decimal
from typing import Optional

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max, Q, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class JournalEntry(models.Model):
    """
    Écriture comptable (QuickBooks-like).
    - Scope: pole + company_code (optionnels)
    - Numérotation séquentielle par journal + exercice (fiscal_year)
    - Source générique (content_type/object_id) pour idempotence (paiements, commandes, dons, etc.)
    - Statuts: DRAFT -> POSTED (verrouillé) / VOID (annulé)
    """

    class Pole(models.TextChoices):
        ECONOMIC = "ECONOMIC", _("Économique")
        SOCIAL = "SOCIAL", _("Social")
        INSTITUTION = "INSTITUTION", _("Institution")
        CORE = "CORE", _("Core")

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Brouillon")
        POSTED = "POSTED", _("Posté")
        REVERSED = "REVERSED", _("Contre-passé")
        VOID = "VOID", _("Annulé")

    class Kind(models.TextChoices):
        GENERAL = "GENERAL", _("Général")
        PAYMENT = "PAYMENT", _("Paiement")
        INVOICE = "INVOICE", _("Facture")
        BILL = "BILL", _("Facture fournisseur")
        REFUND = "REFUND", _("Remboursement")
        ADJUSTMENT = "ADJUSTMENT", _("Ajustement")
        TRANSFER = "TRANSFER", _("Transfert")


    uuid = models.UUIDField(default=uuidlib.uuid4, unique=True, editable=False, db_index=True)

    journal = models.ForeignKey(
        "accounting.Journal",
        on_delete=models.PROTECT,
        related_name="entries",
        db_index=True,
    )

    pole = models.CharField(
        max_length=16,
        choices=Pole.choices,
        blank=True,
        default="",
        db_index=True,
    )

    company_code = models.CharField(
        max_length=32,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Entité (optionnel) : ex ECONOMIC-SN / SOCIAL-RW / ..."),
    )

    date = models.DateField(default=timezone.localdate, db_index=True)
    fiscal_year = models.PositiveIntegerField(default=0, db_index=True)

    # Numérotation par journal + exercice
    entry_no = models.PositiveIntegerField(default=0, db_index=True)

    # Référence lisible (doc number)
    reference = models.CharField(max_length=64, blank=True, default="", db_index=True)

    kind = models.CharField(max_length=24, choices=Kind.choices, default=Kind.GENERAL, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)

    memo = models.CharField(max_length=240, blank=True, default="")
    currency = models.CharField(max_length=8, default="XOF", help_text=_("Devise (reporting/écriture)."))

    # Totaux (dénormalisés)
    total_debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total_credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    # Lien générique vers la source (PaymentIntent, Order, Donation, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=64, blank=True, default="")
    content_object = GenericForeignKey("content_type", "object_id")

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    voided_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["journal", "fiscal_year", "entry_no"]),
            models.Index(fields=["status", "date"]),
            models.Index(fields=["pole", "company_code", "date"]),
            models.Index(fields=["kind", "date"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["journal", "fiscal_year", "entry_no"],
                name="uniq_entry_journal_year_no",
                condition=~Q(entry_no=0),
            ),
            models.UniqueConstraint(
                fields=["content_type", "object_id", "kind"],
                name="uniq_entry_source_kind",
                condition=Q(content_type__isnull=False) & ~Q(object_id=""),
            ),
            models.CheckConstraint(
                condition=~Q(reference=""),
                name="ck_entry_reference_not_empty",
            ),
        ]

    def __str__(self) -> str:
        ref = self.reference or str(self.uuid)
        return f"{ref} ({self.journal.code})"

    # Compat anciennes checks
    @property
    def is_posted(self) -> bool:
        return self.status == self.Status.POSTED

    @property
    def is_locked(self) -> bool:
        return self.status in {self.Status.POSTED, self.Status.VOID}

    def save(self, *args, **kwargs):
        self.pole = (self.pole or "").strip().upper()
        self.company_code = (self.company_code or "").strip().upper()
        self.currency = (self.currency or "XOF").upper()
        self.memo = (self.memo or "").strip()

        if not self.fiscal_year:
            self.fiscal_year = int((self.date or timezone.localdate()).year)

        if not self.reference:
            ym = timezone.now().strftime("%Y%m")
            tail = str(self.uuid).split("-")[0].upper()
            self.reference = f"JE-{ym}-{tail}"

        # Numérotation séquentielle si nouvelle écriture et entry_no vide
        if self.pk is None and not self.entry_no:
            with transaction.atomic():
                last = (
                    JournalEntry.objects.select_for_update()
                    .filter(journal_id=self.journal_id, fiscal_year=self.fiscal_year)
                    .aggregate(m=Max("entry_no"))
                    .get("m")
                    or 0
                )
                self.entry_no = int(last) + 1
                super().save(*args, **kwargs)
            return

        super().save(*args, **kwargs)

    # ----------------------------
    # Calculs / validations
    # ----------------------------
    def recalc_totals(self, *, save: bool = True) -> tuple[Decimal, Decimal]:
        agg = self.lines.aggregate(
            d=Sum("debit"),
            c=Sum("credit"),
        )
        d = Decimal(agg.get("d") or 0)
        c = Decimal(agg.get("c") or 0)

        self.total_debit = d
        self.total_credit = c

        if save:
            self.save(update_fields=["total_debit", "total_credit", "updated_at"])
        return d, c

    def clean(self):
        super().clean()

        self.pole = (self.pole or "").strip().upper()
        self.company_code = (self.company_code or "").strip().upper()
        self.currency = (self.currency or "XOF").upper()

        if self.is_locked:
            raise ValidationError(_("Impossible de modifier une écriture postée/annulée (verrouillée)."))

        if not self.date:
            raise ValidationError({"date": _("La date est requise.")})

        if not self.journal_id:
            raise ValidationError({"journal": _("Le journal est requis.")})

    def validate_balanced(self) -> None:
        d, c = self.recalc_totals(save=False)
        if d <= 0 or c <= 0:
            raise ValidationError(_("Une écriture doit avoir des montants > 0."))
        if d != c:
            raise ValidationError(_("Écriture non équilibrée (débit != crédit)."))

    # ----------------------------
    # Workflow
    # ----------------------------
    @transaction.atomic
    def post(self) -> None:
        """
        Poste l'écriture (verrouille).
        """
        self.refresh_from_db()

        if self.status == self.Status.POSTED:
            return
        if self.status == self.Status.VOID:
            raise ValidationError(_("Impossible de poster une écriture annulée."))

        # Re-valide équilibre
        self.validate_balanced()

        self.status = self.Status.POSTED
        self.posted_at = timezone.now()
        self.save(update_fields=["status", "posted_at", "updated_at", "total_debit", "total_credit"])

    @transaction.atomic
    def void(self, *, reason: str = "") -> None:
        """
        Annule (VOID) une écriture postée ou brouillon (verrouille).
        """
        self.refresh_from_db()

        if self.status == self.Status.VOID:
            return

        self.status = self.Status.VOID
        self.voided_at = timezone.now()
        if reason:
            md = dict(self.metadata or {})
            md["void_reason"] = reason
            self.metadata = md
            self.save(update_fields=["status", "voided_at", "metadata", "updated_at"])
        else:
            self.save(update_fields=["status", "voided_at", "updated_at"])

    # ----------------------------
    # Idempotence helper
    # ----------------------------
    @classmethod
    def get_existing_for_source(cls, *, content_object, kind: str) -> Optional["JournalEntry"]:
        ct = ContentType.objects.get_for_model(content_object.__class__)
        obj_id = str(getattr(content_object, "pk", "") or getattr(content_object, "id", "") or "")
        if not obj_id:
            return None
        return cls.objects.filter(content_type=ct, object_id=obj_id, kind=kind).first()







# # accounting/models/journal_entry.py
# from __future__ import annotations

# import uuid as uuidlib
# from decimal import Decimal

# from django.conf import settings
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
# from django.core.exceptions import ValidationError

# from django.db import models, transaction
# from django.db.models import Q, Sum

# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .sequence import AccountingSequence


# class JournalEntry(models.Model):
#     class Status(models.TextChoices):
#         DRAFT = "DRAFT", _("Brouillon")
#         POSTED = "POSTED", _("Comptabilisé")
#         REVERSED = "REVERSED", _("Contre-passé")
#         VOID = "VOID", _("Annulé")


#     class Kind(models.TextChoices):
#         PAYMENT = "PAYMENT", _("Paiement")
#         REFUND = "REFUND", _("Remboursement")
#         ADJUSTMENT = "ADJUSTMENT", _("Ajustement")
    
#     class Pole(models.TextChoices):
#         ECONOMIC = "ECONOMIC", _("Économique")
#         SOCIAL = "SOCIAL", _("Social")
#         INSTITUTION = "INSTITUTION", _("Institution")
#         CORE = "CORE", _("Core")


#     uuid = models.UUIDField(default=uuidlib.uuid4, unique=True, editable=False, db_index=True)

#     pole = models.CharField(max_length=16, choices=Pole.choices, default=Pole.ECONOMIC, db_index=True)
#     company_code = models.CharField(max_length=32, blank=True, default="", db_index=True)

#     journal = models.ForeignKey("accounting.Journal", on_delete=models.PROTECT, related_name="entries")
#     date = models.DateField(default=timezone.now, db_index=True)

#     reference = models.CharField(max_length=40, blank=True, default="", db_index=True)
#     memo = models.CharField(max_length=240, blank=True, default="")
#     description = models.TextField(blank=True, default="")

#     currency = models.CharField(max_length=8, default="XOF")
#     exchange_rate = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal("1.0"))

#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
#     kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.ADJUSTMENT, db_index=True)

#     total_debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
#     total_credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="accounting_entries_created",
#     )

#     is_posted = models.BooleanField(default=False, db_index=True)

#     posted_at = models.DateTimeField(null=True, blank=True)

#     # lien source (PaymentIntent / Donation / Order / etc.)
#     content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
#     object_id = models.CharField(max_length=64, blank=True, default="")
#     content_object = GenericForeignKey("content_type", "object_id")

#     metadata = models.JSONField(default=dict, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-date", "-id"]
#         indexes = [
#             models.Index(fields=["status", "-date"]),
#             models.Index(fields=["kind", "-date"]),
#             models.Index(fields=["reference"]),
#         ]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["content_type", "object_id", "kind"],
#                 name="uq_accounting_entry_source_kind",
#                 condition=~Q(reference=""),

#             ),
#             models.UniqueConstraint(
#                 fields=["pole", "company_code", "source_content_type", "source_object_id"],
#                 name="uniq_journalentry_source",
#                 condition=~Q(source_object_id=""),
#             ),
#         ]

#     def __str__(self) -> str:
#         return self.reference or str(self.uuid)

#     def save(self, *args, **kwargs):
#         if not self.reference:
#             d = self.date or timezone.now().date()
#             tail = str(self.uuid).split("-")[0].upper()
#             self.reference = f"JE-{self.journal.code}-{d:%Y%m%d}-{tail}"
#         super().save(*args, **kwargs)

#     @property
#     def total_debit(self) -> Decimal:
#         return sum((l.debit for l in self.lines.all()), Decimal("0.00"))

#     @property
#     def total_credit(self) -> Decimal:
#         return sum((l.credit for l in self.lines.all()), Decimal("0.00"))

#     @property
#     def is_balanced(self) -> bool:
#         return self.total_debit == self.total_credit and self.total_debit > 0

#     @transaction.atomic
#     def post(self) -> None:
#         if self.status == self.Status.POSTED:
#             return
#         if not self.is_balanced:
#             raise ValueError("JournalEntry not balanced.")
#         self.status = self.Status.POSTED
#         self.posted_at = timezone.now()
#         self.save(update_fields=["status", "posted_at", "updated_at"])
