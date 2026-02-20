# accounting/models/journal_line.py
from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Q
from django.utils.translation import gettext_lazy as _


class JournalLine(models.Model):
    entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.CASCADE,
        related_name="lines",
        db_index=True,
    )

    line_no = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text=_("Numéro de ligne (auto si 0)."),
    )

    account = models.ForeignKey(
        "accounting.Account",
        on_delete=models.PROTECT,
        related_name="lines",
        db_index=True,
    )

    label = models.CharField(max_length=240, blank=True, default="")

    debit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    currency = models.CharField(max_length=8, blank=True, default="")
    amount_fx = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    customer_ref = models.CharField(max_length=64, blank=True, default="", db_index=True)
    vendor_ref = models.CharField(max_length=64, blank=True, default="", db_index=True)
    project_ref = models.CharField(max_length=64, blank=True, default="", db_index=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["entry_id", "line_no", "id"]
        indexes = [
            models.Index(fields=["account", "created_at"]),
            models.Index(fields=["entry", "line_no"]),
            models.Index(fields=["customer_ref", "created_at"]),
            models.Index(fields=["vendor_ref", "created_at"]),
            models.Index(fields=["project_ref", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["entry", "line_no"], name="uniq_journal_line_entry_lineno"),
            models.CheckConstraint(
                condition=Q(debit__gte=0) & Q(credit__gte=0),
                name="ck_jl_non_negative",
            ),
            models.CheckConstraint(
                condition=(Q(debit__gt=0) & Q(credit=0)) | (Q(credit__gt=0) & Q(debit=0)),
                name="ck_jl_debit_xor_credit",
            ),
        ]

    def __str__(self) -> str:
        side = "D" if (self.debit or 0) > 0 else "C"
        amt = self.debit if (self.debit or 0) > 0 else self.credit
        return f"{self.entry} | {self.account.code} | {side} {amt}"

    @property
    def amount(self) -> Decimal:
        d = Decimal(self.debit or 0)
        c = Decimal(self.credit or 0)
        return d if d > 0 else c

    def clean(self):
        super().clean()

        if self.entry_id:
            st = getattr(self.entry, "status", "")
            if st in ("POSTED", "VOID"):
                raise ValidationError(_("Impossible de modifier une écriture postée/annulée (verrouillée)."))

        d = Decimal(self.debit or 0)
        c = Decimal(self.credit or 0)

        if d < 0 or c < 0:
            raise ValidationError(_("Débit / crédit ne peut pas être négatif."))

        if (d > 0 and c > 0) or (d == 0 and c == 0):
            raise ValidationError(_("Une ligne doit avoir soit un débit, soit un crédit (exclusif)."))

        if self.line_no and self.line_no < 1:
            raise ValidationError({"line_no": _("line_no doit être >= 1 (ou 0 pour auto).")})

        self.currency = (self.currency or "").strip().upper()

        if self.currency and self.amount_fx is None:
            self.amount_fx = self.amount

    def save(self, *args, **kwargs):
        skip_clean = kwargs.pop("skip_clean", False)

        self.debit = self.debit or Decimal("0.00")
        self.credit = self.credit or Decimal("0.00")
        self.label = (self.label or "").strip()
        self.currency = (self.currency or "").strip().upper()

        if self.entry_id and (not self.line_no or self.line_no == 0):
            mx = (
                JournalLine.objects.filter(entry_id=self.entry_id)
                .aggregate(m=Max("line_no"))
                .get("m")
                or 0
            )
            self.line_no = int(mx) + 1

        if self.entry_id and self.line_no:
            exists = JournalLine.objects.filter(entry_id=self.entry_id, line_no=self.line_no)
            if self.pk:
                exists = exists.exclude(pk=self.pk)
            if exists.exists():
                mx = (
                    JournalLine.objects.filter(entry_id=self.entry_id)
                    .aggregate(m=Max("line_no"))
                    .get("m")
                    or 0
                )
                self.line_no = int(mx) + 1

        if not skip_clean:
            self.full_clean()

        return super().save(*args, **kwargs)






# # accounting/models/journal_line.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.db.models import Q
# from django.utils.translation import gettext_lazy as _

# from .account import Account
# from .journal_entry import JournalEntry

# class JournalLine(models.Model):
#     entry = models.ForeignKey("accounting.JournalEntry", on_delete=models.CASCADE, related_name="lines")
#     line_no = models.PositiveIntegerField(default=1, db_index=True)
#     account = models.ForeignKey("accounting.Account", on_delete=models.PROTECT, related_name="lines")

#     label = models.CharField(max_length=240, blank=True, default="")

#     debit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
#     credit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

#     currency = models.CharField(max_length=8, blank=True, default="")  # devise transaction
#     amount_fx = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # montant devise
    
#     # QuickBooks-like dimensions (optionnel)
#     customer_ref = models.CharField(max_length=64, blank=True, default="", db_index=True)
#     vendor_ref = models.CharField(max_length=64, blank=True, default="", db_index=True)
#     project_ref = models.CharField(max_length=64, blank=True, default="", db_index=True)

#     metadata = models.JSONField(default=dict, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)

#     class Meta:
#         ordering = ["entry_id", "line_no", "id"]
#         indexes = [
#             models.Index(fields=["account", "created_at"]),
#             models.Index(fields=["entry", "line_no"]),

#         ]
#         constraints = [
#             models.CheckConstraint(
#                 check=Q(debit__gte=0) & Q(credit__gte=0),
#                 name="ck_line_non_negative",
#             ),
#             models.CheckConstraint(
#                 check=(Q(debit=0) & Q(credit__gt=0)) | (Q(credit=0) & Q(debit__gt=0)),
#                 name="ck_line_debit_xor_credit",
#             ),
#             models.CheckConstraint(check=~(Q(debit__gt=0) & Q(credit__gt=0)), name="jl_not_both"),
#             models.CheckConstraint(check=~(Q(debit=0) & Q(credit=0)), name="jl_not_zero"),
#         ]  
        

#     def __str__(self) -> str:
#         side = "D" if self.debit > 0 else "C"
#         amt = self.debit if self.debit > 0 else self.credit
#         return f"{self.entry} {self.account.code} {side} {amt}"

#     def clean(self):
#         super().clean()
#         d = Decimal(self.debit or 0)
#         c = Decimal(self.credit or 0)
#         if d < 0 or c < 0:
#             raise ValidationError(_("Débit / crédit ne peut pas être négatif."))
#         if (d > 0 and c > 0) or (d == 0 and c == 0):
#             raise ValidationError(_("Une ligne doit avoir soit un débit, soit un crédit (exclusif)."))
#         if self.entry_id and self.entry.is_posted:
#             raise ValidationError(_("Impossible de modifier une écriture postée (verrouillée)."))


#     def save(self, *args, **kwargs):
#         self.debit = self.debit or Decimal("0.00")
#         self.credit = self.credit or Decimal("0.00")
#         super().save(*args, **kwargs)