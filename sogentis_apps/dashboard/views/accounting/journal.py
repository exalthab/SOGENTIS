# dashboard/views/accounting/journal.py
from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

try:
    from accounting.models import Journal, JournalEntry  # type: ignore
except Exception:  # pragma: no cover
    Journal = None  # type: ignore
    JournalEntry = None  # type: ignore


def _can_access(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    try:
        return bool(user.has_perm("accounting.view_journal") or user.has_perm("dashboard.access_accounting_space"))
    except Exception:
        return False


def _get_str(request: HttpRequest, key: str, default: str = "") -> str:
    return str(request.GET.get(key, default) or "").strip()


def _posted_value() -> str:
    # essaie JournalEntry.Status.POSTED sinon "POSTED"
    try:
        return getattr(getattr(JournalEntry, "Status", None), "POSTED", "POSTED")
    except Exception:
        return "POSTED"


@login_required
def journal_list_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/journal_list.html", {"denied": True}, status=403)
    if Journal is None:
        raise Http404("Accounting module not available")

    q = _get_str(request, "q")
    pole = _get_str(request, "pole")
    active = _get_str(request, "active", "1")

    qs = Journal.objects.all()
    if active in ("1", "true", "yes", "on"):
        qs = qs.filter(is_active=True)
    elif active in ("0", "false", "no", "off"):
        qs = qs.filter(is_active=False)

    if pole:
        qs = qs.filter(pole=pole.upper())
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))

    qs = qs.order_by("pole", "code", "id")

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(_get_str(request, "page", "1"))

    ctx: Dict[str, Any] = {
        "topbar_title": "Journaux",
        "topbar_subtitle": "Liste des journaux (receipts, sales, etc.).",
        "journals": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "pole": pole,
        "active": active,
        "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Journaux"}],
    }
    return render(request, "dashboard/accounting/journal_list.html", ctx)


@login_required
def journal_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/journal_detail.html", {"denied": True}, status=403)
    if Journal is None:
        raise Http404("Accounting module not available")

    journal = get_object_or_404(Journal, pk=pk)

    entries = []
    entries_count = 0
    if JournalEntry is not None:
        try:
            posted = _posted_value()
            base = (
                JournalEntry.objects.select_related("journal")
                .filter(journal_id=journal.pk)
                .order_by("-date", "-id")
            )
            entries_count = base.count()
            entries = list(base[:30])
        except Exception:
            entries = []
            entries_count = 0

    return render(
        request,
        "dashboard/accounting/journal_detail.html",
        {
            "topbar_title": "Journal",
            "topbar_subtitle": f"{getattr(journal, 'code', '')} — {getattr(journal, 'name', '')}",
            "journal": journal,
            "entries": entries,
            "entries_count": entries_count,
            # pour le bouton “Voir les écritures” (filtrées)
            "entries_qs": {"journal": journal.pk},
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Journaux"}, {"label": getattr(journal, "code", "")}],
        },
    )






# # dashboard/views/accounting/journal.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.shortcuts import get_object_or_404, render

# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)

# def _get_journal_models():
#     try:
#         from accounting.models.journal_entry import JournalEntry  # type: ignore
#         from accounting.models.journal_line import JournalLine  # type: ignore
#         return JournalEntry, JournalLine, True
#     except Exception:
#         return None, None, False


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def journal_list_view(request):
#     JournalEntry, _, ok = _get_journal_models()

#     q = (request.GET.get("q") or "").strip()
#     pole = (request.GET.get("pole") or "").strip().upper()
#     company = (request.GET.get("company") or "").strip().upper()
#     status = (request.GET.get("status") or "").strip()

#     if not ok:
#         return render(request, "dashboard/accounting/journal_list.html", {"journal_available": False})

#     qs = JournalEntry.objects.all()

#     if pole:
#         qs = qs.filter(pole=pole)
#     if company:
#         qs = qs.filter(company_code=company)
#     if status:
#         qs = qs.filter(status=status)
#     if q:
#         qs = qs.filter(Q(reference__icontains=q) | Q(memo__icontains=q) | Q(description__icontains=q))

#     qs = qs.order_by("-date", "-id")

#     paginator = Paginator(qs, 30)
#     page_obj = paginator.get_page(request.GET.get("page") or 1)

#     ctx = {
#         "journal_available": True,
#         "q": q,
#         "pole": pole,
#         "company": company,
#         "status": status,
#         "page_obj": page_obj,
#         "entries": page_obj.object_list,
#         "paginator": paginator,
#         "status_choices": getattr(JournalEntry, "Status", None).choices if hasattr(JournalEntry, "Status") else [],
#     }
#     return render(request, "dashboard/accounting/journal_list.html", ctx)


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def journal_detail_view(request, pk: int):
#     JournalEntry, JournalLine, ok = _get_journal_models()
#     if not ok:
#         return render(request, "dashboard/accounting/journal_detail.html", {"journal_available": False})

#     entry = get_object_or_404(JournalEntry, pk=pk)
#     lines = JournalLine.objects.select_related("account").filter(entry=entry).order_by("line_no", "id")
#     return render(
#         request,
#         "dashboard/accounting/journal_detail.html",
#         {"journal_available": True, "entry": entry, "lines": lines},
#     )
