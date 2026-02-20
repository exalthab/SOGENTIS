# accounting/views/dashboard.py
from __future__ import annotations

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from accounting.permissions.accounting_permissions import accounting_required
from accounting.selectors.dashboard_queries import get_dashboard_kpis


def _parse_date(s: str, default: date) -> date:
    s = (s or "").strip()
    if not s:
        return default
    try:
        return date.fromisoformat(s)
    except Exception:
        return default


def _redirect_with_query(request: HttpRequest, url_name: str) -> HttpResponse:
    url = reverse(url_name)
    qs = request.META.get("QUERY_STRING", "") or ""
    return HttpResponseRedirect(f"{url}?{qs}" if qs else url)


@login_required
@accounting_required
def accounting_dashboard_view(request: HttpRequest) -> HttpResponse:
    pole = str(request.GET.get("pole", "") or "").strip().upper()
    company_code = str(request.GET.get("company_code", "") or "").strip().upper()
    as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())

    kpis = get_dashboard_kpis(pole=pole, company_code=company_code, as_of=as_of)

    return render(
        request,
        "dashboard/accounting/index.html",
        {
            "topbar_title": "Accounting",
            "topbar_subtitle": "Plan comptable, journal, rapports.",
            "pole": pole,
            "company_code": company_code,
            "as_of": as_of,
            "kpis": kpis,
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}],
        },
    )


# --- Dashboard shortcuts -> rapports statutaires (source unique) ---

@login_required
@accounting_required
def balance_sheet_view(request: HttpRequest) -> HttpResponse:
    return _redirect_with_query(request, "accounting:report_balance_sheet")


@login_required
@accounting_required
def trial_balance_shortcut_view(request: HttpRequest) -> HttpResponse:
    return _redirect_with_query(request, "accounting:trial_balance")


@login_required
@accounting_required
def profit_loss_shortcut_view(request: HttpRequest) -> HttpResponse:
    return _redirect_with_query(request, "accounting:report_income_statement")


@login_required
@accounting_required
def cash_flow_shortcut_view(request: HttpRequest) -> HttpResponse:
    return _redirect_with_query(request, "accounting:report_cash_flow")






# # accounting/views/dashboard.py
# from __future__ import annotations

# from datetime import date

# from django.contrib.auth.decorators import login_required
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.utils import timezone

# from accounting.permissions.accounting_permissions import accounting_required
# from accounting.selectors.dashboard_queries import get_dashboard_kpis
# from accounting.services.reporting import run_balance_sheet
# from accounting.models import Account


# def _parse_date(s: str, default: date) -> date:
#     s = (s or "").strip()
#     if not s:
#         return default
#     try:
#         return date.fromisoformat(s)
#     except Exception:
#         return default


# def _get_pole_choices():
#     Pole = getattr(Account, "Pole", None)
#     return getattr(Pole, "choices", ()) if Pole else ()


# @login_required
# @accounting_required
# def accounting_dashboard_view(request: HttpRequest) -> HttpResponse:
#     pole = str(request.GET.get("pole", "") or "").strip().upper()
#     company_code = str(request.GET.get("company_code", "") or "").strip().upper()
#     as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())

#     kpis = get_dashboard_kpis(pole=pole, company_code=company_code, as_of=as_of)

#     return render(
#         request,
#         "dashboard/accounting/index.html",
#         {
#             "topbar_title": "Accounting",
#             "topbar_subtitle": "Plan comptable, journal, rapports.",
#             "pole": pole,
#             "company_code": company_code,
#             "as_of": as_of,
#             "kpis": kpis,
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}],
#         },
#     )


# @login_required
# @accounting_required
# def balance_sheet_view(request: HttpRequest) -> HttpResponse:
#     pole = str(request.GET.get("pole", "") or "").strip().upper()
#     company_code = str(request.GET.get("company_code", "") or "").strip().upper()
#     as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())

#     data = run_balance_sheet(pole=pole, company_code=company_code, as_of=as_of)

#     return render(
#         request,
#         "dashboard/accounting/report_balance_sheet.html",
#         {
#             "topbar_title": "Balance Sheet",
#             "topbar_subtitle": "Actif / Passif / Capitaux propres.",
#             "pole": pole,
#             "company_code": company_code,
#             "as_of": as_of,
#             "pole_choices": _get_pole_choices(),
#             "assets": data["assets"],
#             "liabilities": data["liabilities"],
#             "equity": data["equity"],
#             "total_assets": data["total_assets"],
#             "total_liabilities": data["total_liabilities"],
#             "total_equity": data["total_equity"],
#             "diff": data["diff"],
#             "breadcrumbs": [
#                 {"label": "Dashboard"},
#                 {"label": "Accounting"},
#                 {"label": "Reports"},
#                 {"label": "Balance Sheet"},
#             ],
#         },
#     )




# # accounting/views/dashboard.py
# from __future__ import annotations

# from datetime import date
# from typing import Any, Dict, Tuple

# from django.contrib.auth.decorators import login_required
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.utils import timezone

# from accounting.permissions.accounting_permissions import accounting_required
# from accounting.selectors.dashboard_queries import get_dashboard_kpis
# from accounting.services.reporting import run_balance_sheet


# def _parse_date(s: str, default: date) -> date:
#     s = (s or "").strip()
#     if not s:
#         return default
#     try:
#         return date.fromisoformat(s)
#     except Exception:
#         return default


# @login_required
# @accounting_required
# def accounting_dashboard_view(request: HttpRequest) -> HttpResponse:
#     pole = str(request.GET.get("pole", "") or "").strip().upper()
#     company_code = str(request.GET.get("company_code", "") or "").strip().upper()
#     as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())

#     kpis = get_dashboard_kpis(pole=pole, company_code=company_code, as_of=as_of)

#     return render(
#         request,
#         "dashboard/accounting/index.html",
#         {
#             "topbar_title": "Accounting",
#             "topbar_subtitle": "Plan comptable, journal, rapports.",
#             "pole": pole,
#             "company_code": company_code,
#             "as_of": as_of,
#             "kpis": kpis,
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}],
#         },
#     )


# @login_required
# @accounting_required
# def balance_sheet_view(request: HttpRequest) -> HttpResponse:
#     pole = str(request.GET.get("pole", "") or "").strip().upper()
#     company_code = str(request.GET.get("company_code", "") or "").strip().upper()
#     as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())

#     data = run_balance_sheet(pole=pole, company_code=company_code, as_of=as_of)

#     return render(
#         request,
#         "dashboard/accounting/report_balance_sheet.html",
#         {
#             "topbar_title": "Balance Sheet",
#             "topbar_subtitle": "Actif / Passif / Capitaux propres.",
#             "pole": pole,
#             "company_code": company_code,
#             "as_of": as_of,
#             "pole_choices": getattr(getattr(__import__("accounting.models", fromlist=["Account"]).models, "Account", None), "Pole", None).choices
#             if hasattr(__import__("accounting.models", fromlist=["Account"]).models, "Account") else (),
#             "assets": data["assets"],
#             "liabilities": data["liabilities"],
#             "equity": data["equity"],
#             "total_assets": data["total_assets"],
#             "total_liabilities": data["total_liabilities"],
#             "total_equity": data["total_equity"],
#             "diff": data["diff"],
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Reports"}, {"label": "Balance Sheet"}],
#         },
#     )
