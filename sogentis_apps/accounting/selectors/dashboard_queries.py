# accounting/selectors/dashboard_queries.py
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

from django.db.models import Count, Sum
from django.utils import timezone

from accounting.models import Account, Journal, JournalEntry, JournalLine
from accounting.models.period import AccountingPeriod
from accounting.selectors.report_queries import compute_balance_sheet_totals 


def _posted_entry_filter_kwargs() -> Dict[str, Any]:
    # Supporte status="POSTED" (QB-like). Si tu utilises autre chose, adapte ici.
    return {"status": getattr(JournalEntry.Status, "POSTED", "POSTED")}


def get_dashboard_kpis(
    *,
    pole: str = "",
    company_code: str = "",
    as_of: Optional[date] = None,
) -> Dict[str, Any]:
    pole = (pole or "").strip().upper()
    company_code = (company_code or "").strip().upper()
    as_of = as_of or timezone.now().date()

    acc_qs = Account.objects.all()
    je_qs = JournalEntry.objects.all()
    jl_qs = JournalLine.objects.select_related("account", "entry").all()
    j_qs = Journal.objects.all()
    p_qs = AccountingPeriod.objects.all()

    if pole:
        acc_qs = acc_qs.filter(pole=pole)
        je_qs = je_qs.filter(pole=pole) if hasattr(JournalEntry, "pole") else je_qs
        j_qs = j_qs.filter(pole=pole) if hasattr(Journal, "pole") else j_qs
        p_qs = p_qs.filter(pole=pole)

    if company_code:
        acc_qs = acc_qs.filter(company_code=company_code)
        je_qs = je_qs.filter(company_code=company_code) if hasattr(JournalEntry, "company_code") else je_qs
        p_qs = p_qs.filter(company_code=company_code)

    posted_kwargs = _posted_entry_filter_kwargs()
    if "status" in [f.name for f in JournalEntry._meta.fields]:
        posted_entries = je_qs.filter(**posted_kwargs)
    else:
        posted_entries = je_qs  # fallback

    posted_count = posted_entries.count()

    last_entries = posted_entries.order_by("-date", "-id")[:10]

    open_periods = p_qs.filter(status=AccountingPeriod.Status.OPEN).count()
    closed_periods = p_qs.filter(status=AccountingPeriod.Status.CLOSED).count()

    bs_totals = compute_balance_sheet_totals(pole=pole, company_code=company_code, as_of=as_of)

    sums = jl_qs
    # filter posted entries only if possible
    if "status" in [f.name for f in JournalEntry._meta.fields]:
        sums = sums.filter(entry__status=posted_kwargs["status"])
    sums = sums.filter(entry__date__lte=as_of)

    if pole:
        sums = sums.filter(account__pole=pole)
    if company_code:
        sums = sums.filter(account__company_code=company_code)

    agg = sums.aggregate(
        debit=Sum("debit"),
        credit=Sum("credit"),
    )
    total_debit = agg.get("debit") or Decimal("0.00")
    total_credit = agg.get("credit") or Decimal("0.00")

    return {
        "pole": pole,
        "company_code": company_code,
        "as_of": as_of,
        "accounts_count": acc_qs.count(),
        "journals_count": j_qs.count(),
        "posted_entries_count": posted_count,
        "open_periods": open_periods,
        "closed_periods": closed_periods,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "balance_sheet": bs_totals,
        "last_entries": list(last_entries),
    }
