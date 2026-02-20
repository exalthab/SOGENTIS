# accounting/views/reports/ledger.py
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from accounting.models import Account, JournalLine


def _parse_date(v: str | None) -> date | None:
    if not v:
        return None
    return parse_date(v)


def _dec(v) -> Decimal:
    try:
        return Decimal(v or 0)
    except Exception:
        return Decimal("0.00")


@staff_member_required
def ledger_view(request: HttpRequest, account_id: int) -> HttpResponse:
    account = get_object_or_404(Account, pk=account_id)

    d_from = _parse_date(request.GET.get("from"))
    d_to = _parse_date(request.GET.get("to"))

    lines = (
        JournalLine.objects.select_related("entry", "entry__journal", "account")
        .filter(entry__status="POSTED", account=account)
        .order_by("entry__date", "id")
    )
    if d_from:
        lines = lines.filter(entry__date__gte=d_from)
    if d_to:
        lines = lines.filter(entry__date__lte=d_to)

    running = Decimal("0.00")
    rows = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for l in lines.iterator():
        d = _dec(getattr(l, "debit", 0))
        c = _dec(getattr(l, "credit", 0))
        running += (d - c)
        total_debit += d
        total_credit += c
        label = getattr(l, "label", "") or getattr(l.entry, "memo", "")
        rows.append(
            {
                "date": l.entry.date,
                "ref": l.entry.reference,
                "journal": l.entry.journal.code,
                "label": label,
                "debit": d,
                "credit": c,
                "running": running,
            }
        )

    return render(
        request,
        "accounting/reports/ledger.html",
        {
            "account": account,
            "rows": rows,
            "from": d_from,
            "to": d_to,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": running,
        },
    )
