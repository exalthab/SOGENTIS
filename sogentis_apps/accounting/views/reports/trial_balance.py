# accounting/views/reports/trial_balance.py

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date

from accounting.models import JournalLine


def _parse_date(v: str | None) -> date | None:
    if not v:
        return None
    return parse_date(v)


def _dec(v) -> Decimal:
    try:
        return Decimal(v or 0)
    except Exception:
        return Decimal("0.00")


def _base_posted_lines():
    # Base: posted only
    return (
        JournalLine.objects.select_related("entry", "entry__journal", "account")
        .filter(entry__status="POSTED")
    )


def _apply_filters(lines, d_from: date | None, d_to: date | None, pole: str, q: str):
    if d_from:
        lines = lines.filter(entry__date__gte=d_from)
    if d_to:
        lines = lines.filter(entry__date__lte=d_to)
    if pole:
        lines = lines.filter(account__pole=pole)
    if q:
        lines = lines.filter(Q(account__code__icontains=q) | Q(account__name__icontains=q))
    return lines


@staff_member_required
def trial_balance_view(request: HttpRequest) -> HttpResponse:
    d_from = _parse_date(request.GET.get("from"))
    d_to = _parse_date(request.GET.get("to"))
    pole = (request.GET.get("pole") or "").strip().upper()
    q = (request.GET.get("q") or "").strip()

    lines = _apply_filters(_base_posted_lines(), d_from, d_to, pole, q)

    rows = (
        lines.values(
            "account_id",
            "account__code",
            "account__name",
            "account__type",
            "account__pole",
        )
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .order_by("account__code")
    )

    data = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for r in rows:
        debit = _dec(r.get("debit"))
        credit = _dec(r.get("credit"))
        balance = debit - credit
        data.append(
            {
                "account_id": r["account_id"],
                "code": r["account__code"],
                "name": r["account__name"],
                "type": r["account__type"],
                "pole": r["account__pole"],
                "debit": debit,
                "credit": credit,
                "balance": balance,
            }
        )
        total_debit += debit
        total_credit += credit

    return render(
        request,
        "accounting/reports/trial_balance.html",
        {
            "rows": data,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "total_balance": total_debit - total_credit,
            "from": d_from,
            "to": d_to,
            "pole": pole,
            "q": q,
        },
    )




# # accounting/views/reports/trial_balance.py
# from __future__ import annotations

# from datetime import date
# from typing import Optional

# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.utils.dateparse import parse_date

# from accounting.models import AccountingPeriod  # via period.py (déjà dans ton __init__.py)
# from accounting.services.trial_balance import balance_sheet_service 

# def _staff_or_perm(u) -> bool:
#     # adapte si tu as des perms fines plus tard
#     return bool(u and u.is_authenticated and (u.is_staff or u.is_superuser))


# def _get_str(request: HttpRequest, key: str) -> str:
#     return (request.GET.get(key) or "").strip()


# def _get_bool(request: HttpRequest, key: str, default: bool = False) -> bool:
#     v = _get_str(request, key).lower()
#     if v in {"1", "true", "yes", "on"}:
#         return True
#     if v in {"0", "false", "no", "off"}:
#         return False
#     return default


# def _get_int(request: HttpRequest, key: str) -> Optional[int]:
#     v = _get_str(request, key)
#     if not v:
#         return None
#     try:
#         return int(v)
#     except ValueError:
#         return None


# def _get_date(request: HttpRequest, key: str) -> Optional[date]:
#     v = _get_str(request, key)
#     if not v:
#         return None
#     return parse_date(v)


# @login_required
# @user_passes_test(_staff_or_perm)
# def trial_balance_view(request: HttpRequest) -> HttpResponse:
#     period_id = _get_int(request, "period")
#     date_from = _get_date(request, "from")
#     date_to = _get_date(request, "to")
#     base_currency = _get_str(request, "cur") or None

#     posted_only = _get_bool(request, "posted", True)
#     include_zero = _get_bool(request, "zero", False)

#     periods = AccountingPeriod.objects.all().order_by("-start_date")[:60]

#     report = balance_sheet_service(
#         period_id=period_id,
#         date_from=date_from,
#         date_to=date_to,
#         base_currency=base_currency,
#         posted_only=posted_only,
#         include_zero=include_zero,
#     )

#     context = {
#         "periods": periods,
#         "report": report,
#         "filters": {
#             "period": period_id or "",
#             "from": date_from.isoformat() if date_from else "",
#             "to": date_to.isoformat() if date_to else "",
#             "cur": base_currency or "",
#             "posted": posted_only,
#             "zero": include_zero,
#         },
#     }
#     return render(request, "accounting/reports/trial_balance.html", context)
