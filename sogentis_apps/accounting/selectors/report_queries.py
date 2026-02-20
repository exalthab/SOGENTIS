# accounting/selectors/report_queries.py
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce

from accounting.models import Account, JournalEntry, JournalLine


def _posted_filter(qs):
    field_names = {f.name for f in JournalEntry._meta.fields}
    if "status" in field_names:
        posted = getattr(JournalEntry.Status, "POSTED", "POSTED")
        return qs.filter(entry__status=posted)
    if "is_posted" in field_names:
        return qs.filter(entry__is_posted=True)
    return qs


def _scope_filter(qs, *, pole: str = "", company_code: str = ""):
    if pole:
        qs = qs.filter(account__pole=(pole or "").strip().upper())
    if company_code:
        qs = qs.filter(account__company_code=(company_code or "").strip().upper())
    return qs


def _as_of_filter(qs, *, as_of: date):
    return qs.filter(entry__date__lte=as_of)


def _range_filter(qs, *, start: Optional[date] = None, end: Optional[date] = None):
    if start:
        qs = qs.filter(entry__date__gte=start)
    if end:
        qs = qs.filter(entry__date__lte=end)
    return qs


def compute_trial_balance(
    *,
    pole: str = "",
    company_code: str = "",
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> Dict[str, Any]:
    qs = JournalLine.objects.select_related("account", "entry").all()
    qs = _posted_filter(qs)
    qs = _scope_filter(qs, pole=pole, company_code=company_code)
    qs = _range_filter(qs, start=start, end=end)

    rows = (
        qs.values("account_id")
        .annotate(
            debit=Sum("debit"),
            credit=Sum("credit"),
        )
        .order_by("account_id")
    )

    acc_map = {a.id: a for a in Account.objects.filter(id__in=[r["account_id"] for r in rows])}

    out_rows: List[Dict[str, Any]] = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for r in rows:
        a = acc_map.get(r["account_id"])
        if not a:
            continue
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")
        net = debit - credit
        tb_debit = net if net > 0 else Decimal("0.00")
        tb_credit = (-net) if net < 0 else Decimal("0.00")
        total_debit += tb_debit
        total_credit += tb_credit
        out_rows.append(
            {
                "account": a,
                "debit": tb_debit,
                "credit": tb_credit,
                "net": net,
            }
        )

    return {
        "rows": out_rows,
        "total_debit": total_debit,
        "total_credit": total_credit,
    }


def compute_profit_loss(
    *,
    pole: str = "",
    company_code: str = "",
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> Dict[str, Any]:
    qs = JournalLine.objects.select_related("account", "entry").all()
    qs = _posted_filter(qs)
    qs = _scope_filter(qs, pole=pole, company_code=company_code)
    qs = _range_filter(qs, start=start, end=end)

    # On agrège par compte P&L
    pnl_types = {
        Account.Type.INCOME,
        Account.Type.OTHER_INCOME,
        Account.Type.EXPENSE,
        Account.Type.OTHER_EXPENSE,
        Account.Type.COGS,
    }
    qs = qs.filter(account__type__in=list(pnl_types))

    rows = (
        qs.values("account_id")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .order_by("account_id")
    )
    acc_map = {a.id: a for a in Account.objects.filter(id__in=[r["account_id"] for r in rows])}

    income_total = Decimal("0.00")
    other_income_total = Decimal("0.00")
    expense_total = Decimal("0.00")
    other_expense_total = Decimal("0.00")
    cogs_total = Decimal("0.00")

    out_rows: List[Dict[str, Any]] = []
    for r in rows:
        a = acc_map.get(r["account_id"])
        if not a:
            continue
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")

        if a.type in (Account.Type.INCOME, Account.Type.OTHER_INCOME):
            bal = credit - debit
        else:
            bal = debit - credit

        out_rows.append({"account": a, "balance": bal})

        if a.type == Account.Type.INCOME:
            income_total += bal
        elif a.type == Account.Type.OTHER_INCOME:
            other_income_total += bal
        elif a.type == Account.Type.EXPENSE:
            expense_total += bal
        elif a.type == Account.Type.OTHER_EXPENSE:
            other_expense_total += bal
        elif a.type == Account.Type.COGS:
            cogs_total += bal

    net_profit = (income_total + other_income_total) - (expense_total + other_expense_total + cogs_total)

    return {
        "rows": out_rows,
        "income_total": income_total,
        "other_income_total": other_income_total,
        "expense_total": expense_total,
        "other_expense_total": other_expense_total,
        "cogs_total": cogs_total,
        "net_profit": net_profit,
    }


def compute_balance_sheet(
    *,
    pole: str = "",
    company_code: str = "",
    as_of: date,
) -> Dict[str, Any]:
    qs = JournalLine.objects.select_related("account", "entry").all()
    qs = _posted_filter(qs)
    qs = _scope_filter(qs, pole=pole, company_code=company_code)
    qs = _as_of_filter(qs, as_of=as_of)

    bs_types = {Account.Type.ASSET, Account.Type.LIABILITY, Account.Type.EQUITY}
    qs = qs.filter(account__type__in=list(bs_types))

    rows = (
        qs.values("account_id")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .order_by("account_id")
    )
    acc_map = {a.id: a for a in Account.objects.filter(id__in=[r["account_id"] for r in rows])}

    assets: List[Dict[str, Any]] = []
    liabilities: List[Dict[str, Any]] = []
    equity: List[Dict[str, Any]] = []

    total_assets = Decimal("0.00")
    total_liabilities = Decimal("0.00")
    total_equity = Decimal("0.00")

    for r in rows:
        a = acc_map.get(r["account_id"])
        if not a:
            continue
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")

        if a.type == Account.Type.ASSET:
            bal = debit - credit
            assets.append({"account": a, "balance": bal})
            total_assets += bal
        elif a.type == Account.Type.LIABILITY:
            bal = credit - debit
            liabilities.append({"account": a, "balance": bal})
            total_liabilities += bal
        elif a.type == Account.Type.EQUITY:
            bal = credit - debit
            equity.append({"account": a, "balance": bal})
            total_equity += bal

    # tri lisible: order/code
    def _sort_key(x):
        a = x["account"]
        return (getattr(a, "order", 1000), getattr(a, "code", ""), getattr(a, "id", 0))

    assets.sort(key=_sort_key)
    liabilities.sort(key=_sort_key)
    equity.sort(key=_sort_key)

    diff = total_assets - (total_liabilities + total_equity)

    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "diff": diff,
    }


def compute_balance_sheet_totals(*, pole: str = "", company_code: str = "", as_of: date) -> Dict[str, Any]:
    bs = compute_balance_sheet(pole=pole, company_code=company_code, as_of=as_of)
    return {
        "total_assets": bs["total_assets"],
        "total_liabilities": bs["total_liabilities"],
        "total_equity": bs["total_equity"],
        "diff": bs["diff"],
    }
