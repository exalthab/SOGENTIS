# accounting/views/reports.py
from __future__ import annotations

from .reports.trial_balance import trial_balance_view  # noqa
from .reports.ledger import ledger_view  # noqa
from .reports.exports import trial_balance_csv_view  # noqa

from .reports.balance_sheet import balance_sheet_report_view  # noqa
from .reports.income_statement import income_statement_report_view  # noqa
from .reports.cash_flow import cash_flow_report_view  # noqa



# # accounting/views/reports.py
# from __future__ import annotations

# from datetime import date
# from decimal import Decimal

# from django.contrib.admin.views.decorators import staff_member_required
# from django.db.models import Sum
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import get_object_or_404, render
# from django.utils.dateparse import parse_date
# from django.utils.translation import gettext_lazy as _

# from accounting.models import Account, JournalLine


# def _parse_date(v: str | None) -> date | None:
#     if not v:
#         return None
#     d = parse_date(v)
#     return d


# def _dec(v) -> Decimal:
#     try:
#         return Decimal(v or 0)
#     except Exception:
#         return Decimal("0.00")


# @staff_member_required
# def trial_balance_view(request: HttpRequest) -> HttpResponse:
#     d_from = _parse_date(request.GET.get("from"))
#     d_to = _parse_date(request.GET.get("to"))
#     pole = (request.GET.get("pole") or "").strip().upper()
#     q = (request.GET.get("q") or "").strip()

#     # Base: posted only
#     lines = (
#         JournalLine.objects.select_related("entry", "entry__journal", "account")
#         .filter(entry__status="POSTED")
#     )

#     if d_from:
#         lines = lines.filter(entry__date__gte=d_from)
#     if d_to:
#         lines = lines.filter(entry__date__lte=d_to)
#     if pole:
#         # pole is stored on account and journal (we use account primarily)
#         lines = lines.filter(account__pole=pole)

#     if q:
#         lines = lines.filter(account__code__icontains=q) | lines.filter(account__name__icontains=q)

#     rows = (
#         lines.values(
#             "account_id",
#             "account__code",
#             "account__name",
#             "account__type",
#             "account__pole",
#         )
#         .annotate(debit=Sum("debit"), credit=Sum("credit"))
#         .order_by("account__code")
#     )

#     data = []
#     total_debit = Decimal("0.00")
#     total_credit = Decimal("0.00")

#     for r in rows:
#         debit = _dec(r.get("debit"))
#         credit = _dec(r.get("credit"))
#         balance = debit - credit
#         data.append(
#             {
#                 "account_id": r["account_id"],
#                 "code": r["account__code"],
#                 "name": r["account__name"],
#                 "type": r["account__type"],
#                 "pole": r["account__pole"],
#                 "debit": debit,
#                 "credit": credit,
#                 "balance": balance,
#             }
#         )
#         total_debit += debit
#         total_credit += credit

#     ctx = {
#         "rows": data,
#         "total_debit": total_debit,
#         "total_credit": total_credit,
#         "total_balance": total_debit - total_credit,
#         "from": d_from,
#         "to": d_to,
#         "pole": pole,
#         "q": q,
#     }
#     return render(request, "accounting/reports/trial_balance.html", ctx)


# @staff_member_required
# def ledger_view(request: HttpRequest, account_id: int) -> HttpResponse:
#     account = get_object_or_404(Account, pk=account_id)

#     d_from = _parse_date(request.GET.get("from"))
#     d_to = _parse_date(request.GET.get("to"))

#     lines = (
#         JournalLine.objects.select_related("entry", "entry__journal", "account")
#         .filter(entry__status="POSTED", account=account)
#         .order_by("entry__date", "id")
#     )
#     if d_from:
#         lines = lines.filter(entry__date__gte=d_from)
#     if d_to:
#         lines = lines.filter(entry__date__lte=d_to)

#     running = Decimal("0.00")
#     rows = []
#     total_debit = Decimal("0.00")
#     total_credit = Decimal("0.00")

#     for l in lines.iterator():
#         d = _dec(l.debit)
#         c = _dec(l.credit)
#         running += (d - c)
#         total_debit += d
#         total_credit += c
#         rows.append(
#             {
#                 "date": l.entry.date,
#                 "ref": l.entry.reference,
#                 "journal": l.entry.journal.code,
#                 "label": l.label or l.entry.memo,
#                 "debit": d,
#                 "credit": c,
#                 "running": running,
#             }
#         )

#     return render(
#         request,
#         "accounting/reports/ledger.html",
#         {
#             "account": account,
#             "rows": rows,
#             "from": d_from,
#             "to": d_to,
#             "total_debit": total_debit,
#             "total_credit": total_credit,
#             "closing_balance": running,
#         },
#     )


# @staff_member_required
# def trial_balance_csv_view(request: HttpRequest) -> HttpResponse:
#     # same filters as HTML
#     d_from = _parse_date(request.GET.get("from"))
#     d_to = _parse_date(request.GET.get("to"))
#     pole = (request.GET.get("pole") or "").strip().upper()
#     q = (request.GET.get("q") or "").strip()

#     lines = JournalLine.objects.select_related("entry", "account").filter(entry__status="POSTED")
#     if d_from:
#         lines = lines.filter(entry__date__gte=d_from)
#     if d_to:
#         lines = lines.filter(entry__date__lte=d_to)
#     if pole:
#         lines = lines.filter(account__pole=pole)
#     if q:
#         lines = lines.filter(account__code__icontains=q) | lines.filter(account__name__icontains=q)

#     rows = (
#         lines.values("account__code", "account__name", "account__type", "account__pole")
#         .annotate(debit=Sum("debit"), credit=Sum("credit"))
#         .order_by("account__code")
#     )

#     def esc(s: str) -> str:
#         s = (s or "").replace('"', '""')
#         return f'"{s}"'

#     out = []
#     out.append("code,name,type,pole,debit,credit,balance")
#     for r in rows:
#         debit = _dec(r.get("debit"))
#         credit = _dec(r.get("credit"))
#         bal = debit - credit
#         out.append(
#             ",".join(
#                 [
#                     esc(str(r.get("account__code") or "")),
#                     esc(str(r.get("account__name") or "")),
#                     esc(str(r.get("account__type") or "")),
#                     esc(str(r.get("account__pole") or "")),
#                     str(debit),
#                     str(credit),
#                     str(bal),
#                 ]
#             )
#         )

#     resp = HttpResponse("\n".join(out), content_type="text/csv; charset=utf-8")
#     resp["Content-Disposition"] = 'attachment; filename="trial_balance.csv"'
#     return resp
