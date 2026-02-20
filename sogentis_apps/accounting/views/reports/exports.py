# accounting/views/reports/exports.py
from __future__ import annotations

from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.db.models import Sum

from .trial_balance import _apply_filters, _base_posted_lines, _dec, _parse_date


@staff_member_required
def trial_balance_csv_view(request: HttpRequest) -> HttpResponse:
    d_from = _parse_date(request.GET.get("from"))
    d_to = _parse_date(request.GET.get("to"))
    pole = (request.GET.get("pole") or "").strip().upper()
    q = (request.GET.get("q") or "").strip()

    lines = _apply_filters(_base_posted_lines(), d_from, d_to, pole, q)

    rows = (
        lines.values("account__code", "account__name", "account__type", "account__pole")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .order_by("account__code")
    )

    def esc(s: str) -> str:
        s = (s or "").replace('"', '""')
        return f'"{s}"'

    out = ["code,name,type,pole,debit,credit,balance"]
    for r in rows:
        debit = _dec(r.get("debit"))
        credit = _dec(r.get("credit"))
        bal = debit - credit
        out.append(
            ",".join(
                [
                    esc(str(r.get("account__code") or "")),
                    esc(str(r.get("account__name") or "")),
                    esc(str(r.get("account__type") or "")),
                    esc(str(r.get("account__pole") or "")),
                    str(debit),
                    str(credit),
                    str(bal),
                ]
            )
        )

    resp = HttpResponse("\n".join(out), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="trial_balance.csv"'
    return resp
