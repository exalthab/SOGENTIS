# accounting/views/reports/income_statement.py
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from accounting.models import Account

try:
    from accounting.services.reporting import run_income_statement  # type: ignore
except Exception:
    run_income_statement = None  # type: ignore


def _parse_date(v: str | None, default: date) -> date:
    v = (v or "").strip()
    if not v:
        return default
    d = parse_date(v)
    return d or default


def _dec(v) -> Decimal:
    try:
        return Decimal(v or 0)
    except Exception:
        return Decimal("0.00")


def _get_pole_choices():
    Pole = getattr(Account, "Pole", None)
    return getattr(Pole, "choices", ()) if Pole else ()


@staff_member_required
def income_statement_report_view(request: HttpRequest) -> HttpResponse:
    pole = str(request.GET.get("pole", "") or "").strip().upper()
    company_code = str(request.GET.get("company_code", "") or request.GET.get("company", "") or "").strip().upper()
    currency = str(request.GET.get("currency", "") or "").strip().upper()

    today = timezone.now().date()
    to_date = _parse_date(request.GET.get("to") or request.GET.get("as_of"), today)
    from_default = to_date.replace(month=1, day=1)
    from_date = _parse_date(request.GET.get("from") or request.GET.get("date_from"), from_default)

    if from_date > to_date:
        from_date, to_date = to_date, from_date

    data: dict = {
        "revenues": [],
        "expenses": [],
        "cogs": [],
        "total_revenues": Decimal("0.00"),
        "total_expenses": Decimal("0.00"),
        "total_cogs": Decimal("0.00"),
        "net_income": Decimal("0.00"),
    }

    if run_income_statement:
        try:
            data = run_income_statement(
                pole=pole,
                company_code=company_code,
                from_date=from_date,
                to_date=to_date,
                currency=currency,
            )
        except TypeError:
            data = run_income_statement(
                pole=pole,
                company_code=company_code,
                from_date=from_date,
                to_date=to_date,
            )

    income_rows = data.get("income_rows") or data.get("revenues") or []
    cogs_rows = data.get("cogs_rows") or data.get("cogs") or []
    expense_rows = data.get("expense_rows") or data.get("expenses") or []

    totals = data.get("totals") or {}
    if not totals:
        total_income = _dec(data.get("total_revenues"))
        total_cogs = _dec(data.get("total_cogs"))
        total_expenses = _dec(data.get("total_expenses"))
        net_income = _dec(data.get("net_income"))
        if net_income == Decimal("0.00") and (total_income or total_cogs or total_expenses):
            net_income = total_income - total_cogs - total_expenses
        totals = {
            "income": total_income,
            "cogs": total_cogs,
            "expenses": total_expenses,
            "net_income": net_income,
        }

    ctx = {
        "pole": pole,
        "company_code": company_code,
        "currency": currency,
        "pole_choices": _get_pole_choices(),
        "date_from": from_date,
        "date_to": to_date,
        "from": from_date,
        "to": to_date,
        "as_of": to_date,
        "income_rows": income_rows,
        "cogs_rows": cogs_rows,
        "expense_rows": expense_rows,
        "totals": totals,
        "revenues": income_rows,
        "expenses": expense_rows,
        "cogs": cogs_rows,
        "total_revenues": totals.get("income", Decimal("0.00")),
        "total_cogs": totals.get("cogs", Decimal("0.00")),
        "total_expenses": totals.get("expenses", Decimal("0.00")),
        "net_income": totals.get("net_income", Decimal("0.00")),
    }
    return render(request, "accounting/reports/income_statement.html", ctx)







# # accounting/views/reports/income_statement.py
# from __future__ import annotations

# from datetime import date

# from django.contrib.admin.views.decorators import staff_member_required
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.utils import timezone

# try:
#     from accounting.services.reporting import run_income_statement  # type: ignore
# except Exception:  # pragma: no cover
#     run_income_statement = None  # type: ignore


# def _parse_date(s: str, default: date) -> date:
#     s = (s or "").strip()
#     if not s:
#         return default
#     try:
#         return date.fromisoformat(s)
#     except Exception:
#         return default


# @staff_member_required
# def income_statement_report_view(request: HttpRequest) -> HttpResponse:
#     pole = str(request.GET.get("pole", "") or "").strip().upper()
#     company_code = str(request.GET.get("company_code", "") or "").strip().upper()
#     as_of = _parse_date(str(request.GET.get("as_of", "") or ""), timezone.now().date())
#     from_date = _parse_date(str(request.GET.get("from", "") or ""), as_of.replace(month=1, day=1))

#     data = {
#         "revenues": [],
#         "expenses": [],
#         "total_revenues": 0,
#         "total_expenses": 0,
#         "net_income": 0,
#     }
#     if run_income_statement:
#         data = run_income_statement(pole=pole, company_code=company_code, from_date=from_date, to_date=as_of)

#     return render(
#         request,
#         "accounting/reports/income_statement.html",
#         {
#             "pole": pole,
#             "company_code": company_code,
#             "from": from_date,
#             "to": as_of,
#             **data,
#         },
#     )
