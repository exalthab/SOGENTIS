# accounting/views/reports/balance_sheet.py
from __future__ import annotations

from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

# Optional: service exists in your codebase (already used in dashboard.py)
try:
    from accounting.services.reporting import run_balance_sheet  # type: ignore
except Exception:  # pragma: no cover
    run_balance_sheet = None  # type: ignore


def _parse_date(s: str, default: date) -> date:
    s = (s or "").strip()
    if not s:
        return default
    try:
        return date.fromisoformat(s)
    except Exception:
        return default


@staff_member_required
def balance_sheet_report_view(request: HttpRequest) -> HttpResponse:
    pole = str(request.GET.get("pole", "") or "").strip().upper()
    company_code = str(request.GET.get("company_code", "") or "").strip().upper()
    as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())

    data = {
        "assets": [],
        "liabilities": [],
        "equity": [],
        "total_assets": 0,
        "total_liabilities": 0,
        "total_equity": 0,
        "diff": 0,
    }
    if run_balance_sheet:
        data = run_balance_sheet(pole=pole, company_code=company_code, as_of=as_of)

    return render(
        request,
        "accounting/reports/balance_sheet.html",
        {
            "pole": pole,
            "company_code": company_code,
            "as_of": as_of,
            **data,
        },
    )
