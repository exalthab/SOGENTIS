# dashboard/views/accounting/index.py
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def _can_access_accounting(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    # permissions optionnels (ne casse pas si absents)
    try:
        return bool(
            user.has_perm("accounting.view_account")
            or user.has_perm("accounting.view_journalentry")
            or user.has_perm("dashboard.access_accounting_space")
        )
    except Exception:
        return False


@login_required
def accounting_index_view(request: HttpRequest) -> HttpResponse:
    if not _can_access_accounting(request.user):
        # Tu peux remplacer par une page 403 dédiée si tu veux
        return render(
            request,
            "dashboard/accounting/index.html",
            {
                "topbar_title": "Accounting",
                "topbar_subtitle": "Accès restreint",
                "accounting_denied": True,
            },
            status=403,
        )

    return render(
        request,
        "dashboard/accounting/index.html",
        {
            "topbar_title": "Accounting",
            "topbar_subtitle": "Plan comptable, journal, rapports.",
            "breadcrumbs": [
                {"label": "Dashboard"},
                {"label": "Accounting"},
            ],
        },
    )







# # dashboard/views/accounting/index.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.shortcuts import render
# from django.utils import timezone

# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)

# def accounting_index_view(request):
#     ctx = {
#         "now": timezone.now(),
#         "accounts_count": 0,
#         "journals_count": 0,
#         "entries_count": 0,
#         "posted_count": 0,
#         "recent_entries": [],
#     }

#     try:
#         from accounting.models import Account, Journal, JournalEntry  # type: ignore

#         ctx["accounts_count"] = Account.objects.count()
#         ctx["journals_count"] = Journal.objects.count()
#         ctx["entries_count"] = JournalEntry.objects.count()
#         ctx["posted_count"] = JournalEntry.objects.filter(status=getattr(JournalEntry.Status, "POSTED", "POSTED")).count()
#         ctx["recent_entries"] = (
#             JournalEntry.objects.select_related("journal")
#             .order_by("-date", "-id")[:12]
#         )
#     except Exception:
#         pass

#     return render(request, "dashboard/accounting/index.html", ctx)
