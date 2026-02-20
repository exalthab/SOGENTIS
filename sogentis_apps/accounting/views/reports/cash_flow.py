# accounting/views/reports/cash_flow.py
from __future__ import annotations

from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

try:
    from accounting.services.reporting import run_cash_flow  # type: ignore
except Exception:  # pragma: no cover
    run_cash_flow = None  # type: ignore


def _parse_date(s: str, default: date) -> date:
    s = (s or "").strip()
    if not s:
        return default
    try:
        return date.fromisoformat(s)
    except Exception:
        return default


@staff_member_required
def cash_flow_report_view(request: HttpRequest) -> HttpResponse:
    pole = str(request.GET.get("pole", "") or "").strip().upper()
    company_code = str(request.GET.get("company_code", "") or "").strip().upper()
    as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())
    from_date = _parse_date(str(request.GET.get("from", "") or ""), as_of.replace(month=1, day=1))

    data = {
        "operating": [],
        "investing": [],
        "financing": [],
        "net_change": 0,
    }
    if run_cash_flow:
        data = run_cash_flow(pole=pole, company_code=company_code, from_date=from_date, to_date=as_of)

    return render(
        request,
        "accounting/reports/cash_flow.html",
        {
            "pole": pole,
            "company_code": company_code,
            "from": from_date,
            "to": as_of,
            **data,
        },
    )
