# dashboard/views/accounting/journal_entries.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

try:
    from accounting.models import Journal, JournalEntry, JournalLine  # type: ignore
except Exception:  # pragma: no cover
    Journal = None  # type: ignore
    JournalEntry = None  # type: ignore
    JournalLine = None  # type: ignore


def _can_access(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    try:
        return bool(user.has_perm("accounting.view_journalentry") or user.has_perm("dashboard.access_accounting_space"))
    except Exception:
        return False


def _get_str(request: HttpRequest, key: str, default: str = "") -> str:
    return str(request.GET.get(key, default) or "").strip()


def _posted_value() -> str:
    try:
        return getattr(getattr(JournalEntry, "Status", None), "POSTED", "POSTED")
    except Exception:
        return "POSTED"


@login_required
def entries_list_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/entries_list.html", {"denied": True}, status=403)
    if JournalEntry is None:
        raise Http404("Accounting module not available")

    q = _get_str(request, "q")
    status = _get_str(request, "status")
    journal_id = _get_str(request, "journal")
    pole = _get_str(request, "pole")
    dt_from = parse_date(_get_str(request, "from"))
    dt_to = parse_date(_get_str(request, "to"))
    only_posted = _get_str(request, "posted", "")

    qs = JournalEntry.objects.select_related("journal").all()

    if journal_id.isdigit():
        qs = qs.filter(journal_id=int(journal_id))
    if pole:
        # si ton JournalEntry a pole, sinon fallback via journal.pole
        if hasattr(JournalEntry, "pole"):
            qs = qs.filter(pole=pole.upper())
        else:
            qs = qs.filter(journal__pole=pole.upper())

    if status:
        qs = qs.filter(status=status)

    if only_posted in ("1", "true", "yes", "on"):
        qs = qs.filter(status=_posted_value())

    if dt_from:
        qs = qs.filter(date__gte=dt_from)
    if dt_to:
        qs = qs.filter(date__lte=dt_to)

    if q:
        # champs possibles: reference/memo/object_id
        qf = Q()
        if hasattr(JournalEntry, "reference"):
            qf |= Q(reference__icontains=q)
        qf |= Q(memo__icontains=q)
        if hasattr(JournalEntry, "object_id"):
            qf |= Q(object_id__icontains=q)
        qs = qs.filter(qf)

    qs = qs.order_by("-date", "-id")

    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(_get_str(request, "page", "1"))

    journals = []
    if Journal is not None:
        try:
            journals = list(Journal.objects.filter(is_active=True).order_by("pole", "code"))
        except Exception:
            journals = []

    ctx: Dict[str, Any] = {
        "topbar_title": "Écritures",
        "topbar_subtitle": "Journal entries (draft/posted).",
        "entries": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "status": status,
        "journal": journal_id,
        "pole": pole,
        "from": dt_from.isoformat() if isinstance(dt_from, date) else "",
        "to": dt_to.isoformat() if isinstance(dt_to, date) else "",
        "posted": only_posted,
        "journals": journals,
        "status_choices": getattr(getattr(JournalEntry, "Status", None), "choices", ()),
        "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Entries"}],
    }
    return render(request, "dashboard/accounting/entries_list.html", ctx)


@login_required
def entry_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/entry_detail.html", {"denied": True}, status=403)
    if JournalEntry is None:
        raise Http404("Accounting module not available")

    entry = get_object_or_404(JournalEntry.objects.select_related("journal"), pk=pk)

    lines = []
    if JournalLine is not None:
        try:
            lines = list(JournalLine.objects.select_related("account").filter(entry_id=entry.pk).order_by("line_no", "id"))
        except Exception:
            lines = []

    # Totaux (safe)
    debit_total = 0
    credit_total = 0
    try:
        for ln in lines:
            debit_total += float(getattr(ln, "debit", 0) or 0)
            credit_total += float(getattr(ln, "credit", 0) or 0)
    except Exception:
        pass

    return render(
        request,
        "dashboard/accounting/entry_detail.html",
        {
            "topbar_title": "Écriture",
            "topbar_subtitle": getattr(entry, "reference", None) or f"#{entry.pk}",
            "entry": entry,
            "lines": lines,
            "debit_total": debit_total,
            "credit_total": credit_total,
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Entries"}, {"label": str(getattr(entry, "reference", entry.pk))}],
        },
    )








# # dashboard/views/accounting/entries.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.shortcuts import get_object_or_404, render


# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)

# @login_required
# @permission_required("accounting.view_account", raise_exception=True)

# def entries_list_view(request):
#     q = (request.GET.get("q") or "").strip()
#     status = (request.GET.get("status") or "").strip().upper()
#     pole = (request.GET.get("pole") or "").strip().upper()
#     per_page = int((request.GET.get("per_page") or "25") or 25)

#     try:
#         from accounting.models import JournalEntry  # type: ignore

#         qs = JournalEntry.objects.select_related("journal").all().order_by("-date", "-id")
#         if q:
#             qs = qs.filter(Q(memo__icontains=q) | Q(reference__icontains=q))
#         if status:
#             qs = qs.filter(status=status)
#         if pole:
#             qs = qs.filter(journal__pole=pole)

#         paginator = Paginator(qs, per_page)
#         page_obj = paginator.get_page(request.GET.get("page") or 1)

#         ctx = {
#             "q": q,
#             "status": status,
#             "pole": pole,
#             "per_page": per_page,
#             "paginator": paginator,
#             "page_obj": page_obj,
#             "entries": page_obj.object_list,
#             "status_choices": getattr(JournalEntry.Status, "choices", ()),
#         }
#     except Exception:
#         ctx = {"q": q, "status": status, "pole": pole, "per_page": per_page, "entries": []}

#     return render(request, "dashboard/accounting/entries_list.html", ctx)


# @staff_required
# def entry_detail_view(request, pk: int):
#     from accounting.models import JournalEntry  # type: ignore
#     e = get_object_or_404(JournalEntry.objects.select_related("journal").prefetch_related("lines__account"), pk=pk)
#     return render(request, "dashboard/accounting/entry_detail.html", {"entry": e})
