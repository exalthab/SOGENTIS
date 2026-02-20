# dashboard/views/accounting/reports.py
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def _can_access(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    try:
        return bool(
            user.has_perm("accounting.view_journalentry")
            or user.has_perm("dashboard.access_accounting_space")
        )
    except Exception:
        return False


def _redirect_with_query(request: HttpRequest, url_name: str) -> HttpResponseRedirect:
    url = reverse(url_name)
    qs = request.META.get("QUERY_STRING", "") or ""
    return HttpResponseRedirect(f"{url}?{qs}" if qs else url)


@login_required
def reports_home_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/reports_home.html", {"denied": True}, status=403)

    return render(
        request,
        "dashboard/accounting/reports_home.html",
        {
            "topbar_title": "Rapports",
            "topbar_subtitle": "Balance, résultat, bilan.",
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Reports"}],
        },
    )


# ---------------------------------------------------------------------
# Dashboard shortcuts -> rapports statutaires (accounting app = source unique)
# Ces vues existent uniquement pour compatibilité avec dashboard:accounting:*
# ---------------------------------------------------------------------

@login_required
def trial_balance_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/reports_home.html", {"denied": True}, status=403)
    return _redirect_with_query(request, "accounting:trial_balance")


@login_required
def profit_loss_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/reports_home.html", {"denied": True}, status=403)
    return _redirect_with_query(request, "accounting:report_income_statement")


@login_required
def balance_sheet_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/reports_home.html", {"denied": True}, status=403)
    return _redirect_with_query(request, "accounting:report_balance_sheet")


# Optionnel si tu ajoutes la route dashboard reports/cash-flow/
@login_required
def cash_flow_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/reports_home.html", {"denied": True}, status=403)
    return _redirect_with_query(request, "accounting:report_cash_flow")






# # dashboard/views/accounting/reports.py
# from __future__ import annotations

# from datetime import date
# from decimal import Decimal
# from typing import Any, Dict, List, Tuple

# from django.contrib.auth.decorators import login_required
# from django.db.models import F, Q, Sum
# from django.http import Http404, HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.utils.dateparse import parse_date

# try:
#     from accounting.models import Account, JournalEntry, JournalLine  # type: ignore
# except Exception:  # pragma: no cover
#     Account = None  # type: ignore
#     JournalEntry = None  # type: ignore
#     JournalLine = None  # type: ignore


# def _can_access(user) -> bool:
#     if not user or not getattr(user, "is_authenticated", False):
#         return False
#     if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
#         return True
#     try:
#         return bool(user.has_perm("accounting.view_journalentry") or user.has_perm("dashboard.access_accounting_space"))
#     except Exception:
#         return False


# def _get_str(request: HttpRequest, key: str, default: str = "") -> str:
#     return str(request.GET.get(key, default) or "").strip()


# def _posted_value() -> str:
#     try:
#         return getattr(getattr(JournalEntry, "Status", None), "POSTED", "POSTED")
#     except Exception:
#         return "POSTED"


# def _date_range(request: HttpRequest) -> Tuple[date | None, date | None]:
#     d1 = parse_date(_get_str(request, "from"))
#     d2 = parse_date(_get_str(request, "to"))
#     return d1, d2


# @login_required
# def reports_home_view(request: HttpRequest) -> HttpResponse:
#     if not _can_access(request.user):
#         return render(request, "dashboard/accounting/reports_home.html", {"denied": True}, status=403)
#     return render(
#         request,
#         "dashboard/accounting/reports_home.html",
#         {
#             "topbar_title": "Rapports",
#             "topbar_subtitle": "Balance, résultat, bilan.",
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Reports"}],
#         },
#     )


# @login_required
# def trial_balance_view(request: HttpRequest) -> HttpResponse:
#     if not _can_access(request.user):
#         return render(request, "dashboard/accounting/report_trial_balance.html", {"denied": True}, status=403)
#     if Account is None or JournalLine is None or JournalEntry is None:
#         raise Http404("Accounting module not available")

#     pole = _get_str(request, "pole")
#     company_code = _get_str(request, "company_code")
#     only_posted = _get_str(request, "posted", "1")
#     dfrom, dto = _date_range(request)

#     lines = JournalLine.objects.select_related("entry", "account").all()

#     if only_posted in ("1", "true", "yes", "on"):
#         lines = lines.filter(entry__status=_posted_value())

#     if dfrom:
#         lines = lines.filter(entry__date__gte=dfrom)
#     if dto:
#         lines = lines.filter(entry__date__lte=dto)

#     if pole:
#         # pole sur account (plus fiable)
#         lines = lines.filter(account__pole=pole.upper())
#     if company_code:
#         lines = lines.filter(account__company_code=company_code.upper())

#     agg = (
#         lines.values(
#             "account_id",
#             "account__code",
#             "account__name",
#             "account__type",
#             "account__subtype",
#             "account__currency",
#         )
#         .annotate(
#             debit=Sum("debit"),
#             credit=Sum("credit"),
#         )
#         .order_by("account__type", "account__code")
#     )

#     rows: List[Dict[str, Any]] = []
#     total_debit = Decimal("0.00")
#     total_credit = Decimal("0.00")

#     for r in agg:
#         d = r.get("debit") or Decimal("0.00")
#         c = r.get("credit") or Decimal("0.00")
#         total_debit += d
#         total_credit += c
#         rows.append(
#             {
#                 "id": r["account_id"],
#                 "code": r["account__code"],
#                 "name": r["account__name"],
#                 "type": r["account__type"],
#                 "subtype": r.get("account__subtype") or "",
#                 "currency": r.get("account__currency") or "",
#                 "debit": d,
#                 "credit": c,
#                 "balance": d - c,
#             }
#         )

#     return render(
#         request,
#         "dashboard/accounting/report_trial_balance.html",
#         {
#             "topbar_title": "Balance générale",
#             "topbar_subtitle": "Trial Balance",
#             "rows": rows,
#             "total_debit": total_debit,
#             "total_credit": total_credit,
#             "pole": pole,
#             "company_code": company_code,
#             "from": dfrom.isoformat() if dfrom else "",
#             "to": dto.isoformat() if dto else "",
#             "posted": only_posted,
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Reports"}, {"label": "Trial Balance"}],
#         },
#     )


# @login_required
# def profit_loss_view(request: HttpRequest) -> HttpResponse:
#     if not _can_access(request.user):
#         return render(request, "dashboard/accounting/report_profit_loss.html", {"denied": True}, status=403)
#     if Account is None or JournalLine is None or JournalEntry is None:
#         raise Http404("Accounting module not available")

#     pole = _get_str(request, "pole")
#     company_code = _get_str(request, "company_code")
#     only_posted = _get_str(request, "posted", "1")
#     dfrom, dto = _date_range(request)

#     lines = JournalLine.objects.select_related("entry", "account").all()
#     if only_posted in ("1", "true", "yes", "on"):
#         lines = lines.filter(entry__status=_posted_value())
#     if dfrom:
#         lines = lines.filter(entry__date__gte=dfrom)
#     if dto:
#         lines = lines.filter(entry__date__lte=dto)
#     if pole:
#         lines = lines.filter(account__pole=pole.upper())
#     if company_code:
#         lines = lines.filter(account__company_code=company_code.upper())

#     # P&L: INCOME/OTHER_INCOME vs EXPENSE/OTHER_EXPENSE/COGS
#     income_types = {"INCOME", "OTHER_INCOME"}
#     expense_types = {"EXPENSE", "OTHER_EXPENSE", "COGS"}

#     by_acc = (
#         lines.values("account_id", "account__code", "account__name", "account__type")
#         .annotate(debit=Sum("debit"), credit=Sum("credit"))
#         .order_by("account__type", "account__code")
#     )

#     income_rows: List[Dict[str, Any]] = []
#     expense_rows: List[Dict[str, Any]] = []
#     total_income = Decimal("0.00")
#     total_expense = Decimal("0.00")

#     for r in by_acc:
#         typ = r.get("account__type") or ""
#         d = r.get("debit") or Decimal("0.00")
#         c = r.get("credit") or Decimal("0.00")

#         if typ in income_types:
#             amt = c - d  # produits net
#             total_income += amt
#             income_rows.append({"code": r["account__code"], "name": r["account__name"], "amount": amt, "type": typ})
#         elif typ in expense_types:
#             amt = d - c  # charges net
#             total_expense += amt
#             expense_rows.append({"code": r["account__code"], "name": r["account__name"], "amount": amt, "type": typ})

#     net = total_income - total_expense

#     return render(
#         request,
#         "accounting/reports/profit_loss.html",
#         {
#             "topbar_title": "Compte de résultat",
#             "topbar_subtitle": "Profit & Loss",
#             "income_rows": income_rows,
#             "expense_rows": expense_rows,
#             "total_income": total_income,
#             "total_expense": total_expense,
#             "net_income": net,
#             "pole": pole,
#             "company_code": company_code,
#             "from": dfrom.isoformat() if dfrom else "",
#             "to": dto.isoformat() if dto else "",
#             "posted": only_posted,
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Reports"}, {"label": "P&L"}],
#         },
#     )


# @login_required
# def balance_sheet_view(request: HttpRequest) -> HttpResponse:
#     if not _can_access(request.user):
#         return render(request, "dashboard/accounting/report_balance_sheet.html", {"denied": True}, status=403)
#     if Account is None or JournalLine is None or JournalEntry is None:
#         raise Http404("Accounting module not available")

#     pole = _get_str(request, "pole")
#     company_code = _get_str(request, "company_code")
#     only_posted = _get_str(request, "posted", "1")
#     dto = parse_date(_get_str(request, "to"))  # bilan à date (to)

#     lines = JournalLine.objects.select_related("entry", "account").all()
#     if only_posted in ("1", "true", "yes", "on"):
#         lines = lines.filter(entry__status=_posted_value())
#     if dto:
#         lines = lines.filter(entry__date__lte=dto)
#     if pole:
#         lines = lines.filter(account__pole=pole.upper())
#     if company_code:
#         lines = lines.filter(account__company_code=company_code.upper())

#     by_acc = (
#         lines.values("account_id", "account__code", "account__name", "account__type")
#         .annotate(debit=Sum("debit"), credit=Sum("credit"))
#         .order_by("account__type", "account__code")
#     )

#     assets: List[Dict[str, Any]] = []
#     liabilities: List[Dict[str, Any]] = []
#     equity: List[Dict[str, Any]] = []

#     t_assets = Decimal("0.00")
#     t_liab = Decimal("0.00")
#     t_eq = Decimal("0.00")

#     for r in by_acc:
#         typ = r.get("account__type") or ""
#         d = r.get("debit") or Decimal("0.00")
#         c = r.get("credit") or Decimal("0.00")

#         if typ == "ASSET":
#             bal = d - c
#             t_assets += bal
#             assets.append({"code": r["account__code"], "name": r["account__name"], "balance": bal})
#         elif typ == "LIABILITY":
#             bal = c - d
#             t_liab += bal
#             liabilities.append({"code": r["account__code"], "name": r["account__name"], "balance": bal})
#         elif typ == "EQUITY":
#             bal = c - d
#             t_eq += bal
#             equity.append({"code": r["account__code"], "name": r["account__name"], "balance": bal})

#     t_right = t_liab + t_eq

#     return render(
#         request,
#         "accounting/reports/balance_sheet.html",
#         {
#             "topbar_title": "Bilan",
#             "topbar_subtitle": "Balance Sheet",
#             "assets": assets,
#             "liabilities": liabilities,
#             "equity": equity,
#             "total_assets": t_assets,
#             "total_liabilities": t_liab,
#             "total_equity": t_eq,
#             "total_right": t_right,
#             "pole": pole,
#             "company_code": company_code,
#             "to": dto.isoformat() if dto else "",
#             "posted": only_posted,
#             "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Reports"}, {"label": "Balance Sheet"}],
#         },
#     )







# # dashboard/views/accounting/reports.py
# from __future__ import annotations

# from decimal import Decimal

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.db.models import F, Q, Sum
# from django.shortcuts import render


# def _get_report_models():
#     try:
#         from accounting.models.journal_entry import JournalEntry  # type: ignore
#         from accounting.models.journal_line import JournalLine  # type: ignore
#         from accounting.models.account import Account
#         return JournalEntry, JournalLine, Account, True
#     except Exception:
#         return None, None, None, False

# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)

# @login_required
# def reports_home_view(request):
#     return render(request, "dashboard/accounting/reports_home.html", {})


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def trial_balance_view(request):
#     JournalEntry, JournalLine, Account, ok = _get_report_models()
#     if not ok:
#         return render(request, "dashboard/accounting/report_trial_balance.html", {"reports_available": False})

#     pole = (request.GET.get("pole") or "").strip().upper()
#     company = (request.GET.get("company") or "").strip().upper()

#     lines = JournalLine.objects.select_related("account", "entry").filter(entry__is_posted=True)

#     if pole:
#         lines = lines.filter(entry__pole=pole)
#     if company:
#         lines = lines.filter(entry__company_code=company)

#     agg = (
#         lines.values("account_id", "account__code", "account__name", "account__type")
#         .annotate(debit=Sum("debit"), credit=Sum("credit"))
#         .order_by("account__code")
#     )

#     rows = []
#     total_debit = Decimal("0.00")
#     total_credit = Decimal("0.00")

#     for r in agg:
#         d = r["debit"] or Decimal("0.00")
#         c = r["credit"] or Decimal("0.00")
#         total_debit += d
#         total_credit += c
#         rows.append(
#             {
#                 "code": r["account__code"],
#                 "name": r["account__name"],
#                 "type": r["account__type"],
#                 "debit": d,
#                 "credit": c,
#                 "balance": d - c,
#             }
#         )

#     ctx = {
#         "reports_available": True,
#         "pole": pole,
#         "company": company,
#         "rows": rows,
#         "total_debit": total_debit,
#         "total_credit": total_credit,
#         "is_balanced": total_debit == total_credit,
#     }
#     return render(request, "dashboard/accounting/report_trial_balance.html", ctx)


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def profit_loss_view(request):
#     _, JournalLine, _, ok = _get_report_models()
#     if not ok:
#         return render(request, "dashboard/accounting/report_profit_loss.html", {"reports_available": False})

#     pole = (request.GET.get("pole") or "").strip().upper()
#     company = (request.GET.get("company") or "").strip().upper()

#     lines = JournalLine.objects.select_related("account", "entry").filter(entry__is_posted=True)

#     if pole:
#         lines = lines.filter(entry__pole=pole)
#     if company:
#         lines = lines.filter(entry__company_code=company)

#     income = (
#         lines.filter(account__type__in=["INCOME", "OTHER_INCOME"])
#         .aggregate(v=Sum(F("credit") - F("debit")))["v"]
#         or Decimal("0.00")
#     )
#     cogs = (
#         lines.filter(account__type="COGS")
#         .aggregate(v=Sum(F("debit") - F("credit")))["v"]
#         or Decimal("0.00")
#     )
#     expenses = (
#         lines.filter(account__type__in=["EXPENSE", "OTHER_EXPENSE"])
#         .aggregate(v=Sum(F("debit") - F("credit")))["v"]
#         or Decimal("0.00")
#     )

#     ctx = {
#         "reports_available": True,
#         "pole": pole,
#         "company": company,
#         "income": income,
#         "cogs": cogs,
#         "expenses": expenses,
#         "gross_profit": income - cogs,
#         "net_income": income - cogs - expenses,
#     }
#     return render(request, "dashboard/accounting/report_profit_loss.html", ctx)


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def balance_sheet_view(request):
#     _, JournalLine, _, ok = _get_report_models()
#     if not ok:
#         return render(request, "dashboard/accounting/report_balance_sheet.html", {"reports_available": False})

#     pole = (request.GET.get("pole") or "").strip().upper()
#     company = (request.GET.get("company") or "").strip().upper()

#     lines = JournalLine.objects.select_related("account", "entry").filter(entry__is_posted=True)
#     if pole:
#         lines = lines.filter(entry__pole=pole)
#     if company:
#         lines = lines.filter(entry__company_code=company)

#     assets = (
#         lines.filter(account__type="ASSET")
#         .aggregate(v=Sum(F("debit") - F("credit")))["v"]
#         or Decimal("0.00")
#     )
#     liabilities = (
#         lines.filter(account__type="LIABILITY")
#         .aggregate(v=Sum(F("credit") - F("debit")))["v"]
#         or Decimal("0.00")
#     )
#     equity = (
#         lines.filter(account__type="EQUITY")
#         .aggregate(v=Sum(F("credit") - F("debit")))["v"]
#         or Decimal("0.00")
#     )

#     ctx = {
#         "reports_available": True,
#         "pole": pole,
#         "company": company,
#         "assets": assets,
#         "liabilities": liabilities,
#         "equity": equity,
#         "balanced": assets == (liabilities + equity),
#     }
#     return render(request, "dashboard/accounting/report_balance_sheet.html", ctx)
