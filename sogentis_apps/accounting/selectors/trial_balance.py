# # accounting/selectors/trial_balance.py
# from __future__ import annotations

# from dataclasses import dataclass
# from datetime import date
# from decimal import Decimal
# from typing import Iterable, Optional

# from django.db.models import DecimalField, F, Model, Q, Sum, Value
# from django.db.models.functions import Coalesce

# from accounting.models import JournalEntry, JournalLine


# def _has_field(model: type[Model], field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except Exception:
#         return False


# def _entry_date_lookup() -> str:
#     # champs possibles selon ton existant
#     candidates = ["entry_date", "date", "posting_date", "accounting_date"]
#     for f in candidates:
#         if _has_field(JournalEntry, f):
#             return f
#     return "entry_date"  # fallback (sera utilisé dans les filtres)


# def _posted_filter() -> Q:
#     """
#     Compat:
#     - si status existe : status == POSTED (ou enum si dispo)
#     - sinon si posted_at existe : posted_at not null
#     - sinon : aucun filtre
#     """
#     if _has_field(JournalEntry, "status"):
#         posted_val = "POSTED"
#         # si ton model expose un enum, on l'utilise (sans casser si absent)
#         entry_status = getattr(JournalEntry, "EntryStatus", None)
#         if entry_status is not None and hasattr(entry_status, "POSTED"):
#             posted_val = entry_status.POSTED
#         return Q(**{f"entry__status": posted_val})

#     if _has_field(JournalEntry, "posted_at"):
#         return Q(entry__posted_at__isnull=False)

#     return Q()  # pas de filtre


# def _amount_fields() -> tuple[str, str]:
#     # priorité: base_debit/base_credit si présents
#     if _has_field(JournalLine, "base_debit") and _has_field(JournalLine, "base_credit"):
#         return "base_debit", "base_credit"
#     return "debit", "credit"


# @dataclass(frozen=True)
# class TrialBalanceRow:
#     account_id: int
#     account_code: str
#     account_name: str
#     debit: Decimal
#     credit: Decimal

#     @property
#     def net(self) -> Decimal:
#         return (self.debit or Decimal("0")) - (self.credit or Decimal("0"))

#     @property
#     def debit_balance(self) -> Decimal:
#         n = self.net
#         return n if n > 0 else Decimal("0")

#     @property
#     def credit_balance(self) -> Decimal:
#         n = self.net
#         return (-n) if n < 0 else Decimal("0")


# def get_trial_balance_rows(
#     *,
#     date_from: Optional[date] = None,
#     date_to: Optional[date] = None,
#     period_id: Optional[int] = None,
#     base_currency: Optional[str] = None,
#     posted_only: bool = True,
#     include_zero: bool = False,
# ) -> list[TrialBalanceRow]:
#     entry_date_field = _entry_date_lookup()
#     debit_field, credit_field = _amount_fields()

#     qs = JournalLine.objects.select_related("account", "entry")

#     # période (si ton JournalEntry a "period")
#     if period_id and _has_field(JournalEntry, "period"):
#         qs = qs.filter(entry__period_id=period_id)

#     # date range
#     if date_from:
#         qs = qs.filter(**{f"entry__{entry_date_field}__gte": date_from})
#     if date_to:
#         qs = qs.filter(**{f"entry__{entry_date_field}__lte": date_to})

#     # posted only
#     if posted_only:
#         qs = qs.filter(_posted_filter())

#     # devise de base (si champ dispo)
#     if base_currency and _has_field(JournalLine, "base_currency"):
#         qs = qs.filter(base_currency=base_currency)

#     debit_sum = Coalesce(Sum(debit_field), Value(0), output_field=DecimalField(max_digits=18, decimal_places=2))
#     credit_sum = Coalesce(Sum(credit_field), Value(0), output_field=DecimalField(max_digits=18, decimal_places=2))

#     agg = (
#         qs.values("account_id", "account__code", "account__name")
#         .annotate(debit=debit_sum, credit=credit_sum)
#         .order_by("account__code")
#     )

#     rows: list[TrialBalanceRow] = []
#     for r in agg:
#         d = r["debit"] or Decimal("0")
#         c = r["credit"] or Decimal("0")
#         if not include_zero and d == 0 and c == 0:
#             continue
#         rows.append(
#             TrialBalanceRow(
#                 account_id=int(r["account_id"]),
#                 account_code=str(r["account__code"] or ""),
#                 account_name=str(r["account__name"] or ""),
#                 debit=d,
#                 credit=c,
#             )
#         )
#     return rows
