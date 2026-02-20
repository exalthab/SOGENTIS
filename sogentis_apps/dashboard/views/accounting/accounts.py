# dashboard/views/accounting/accounts.py
from __future__ import annotations

from typing import Any, Dict, Optional

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

try:
    from accounting.models import Account, JournalLine  # type: ignore
except Exception:  # pragma: no cover
    Account = None  # type: ignore
    JournalLine = None  # type: ignore


def _can_access(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    try:
        return bool(user.has_perm("accounting.view_account") or user.has_perm("dashboard.access_accounting_space"))
    except Exception:
        return False


def _get_str(request: HttpRequest, key: str, default: str = "") -> str:
    return str(request.GET.get(key, default) or "").strip()


@login_required
def accounts_list_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/accounts_list.html", {"denied": True}, status=403)
    if Account is None:
        raise Http404("Accounting module not available")

    q = _get_str(request, "q")
    pole = _get_str(request, "pole")
    company_code = _get_str(request, "company_code")
    typ = _get_str(request, "type")
    subtype = _get_str(request, "subtype")
    active = _get_str(request, "active", "1")  # 1/0

    qs = Account.objects.all()

    if active in ("1", "true", "yes", "on"):
        qs = qs.filter(is_active=True)
    elif active in ("0", "false", "no", "off"):
        qs = qs.filter(is_active=False)

    if pole:
        qs = qs.filter(pole=pole.upper())
    if company_code:
        qs = qs.filter(company_code=company_code.upper())
    if typ:
        qs = qs.filter(type=typ)
    if subtype:
        qs = qs.filter(subtype=subtype)

    if q:
        qs = qs.filter(
            Q(code__icontains=q)
            | Q(name__icontains=q)
            | Q(account_number__icontains=q)
            | Q(description__icontains=q)
        )

    qs = qs.select_related("parent").order_by("pole", "company_code", "order", "code", "id")

    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(_get_str(request, "page", "1"))

    ctx: Dict[str, Any] = {
        "topbar_title": "Comptabilité",
        "topbar_subtitle": "Plan comptable (Chart of Accounts).",
        "accounts": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "pole": pole,
        "company_code": company_code,
        "type": typ,
        "subtype": subtype,
        "active": active,
        "type_choices": getattr(Account.Type, "choices", ()),
        "subtype_choices": getattr(Account.Subtype, "choices", ()),
        "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Accounts"}],
    }
    return render(request, "dashboard/accounting/accounts_list.html", ctx)


@login_required
def account_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/accounting/account_detail.html", {"denied": True}, status=403)
    if Account is None:
        raise Http404("Accounting module not available")

    acc = get_object_or_404(Account.objects.select_related("parent"), pk=pk)

    children = (
        Account.objects.filter(parent_id=acc.pk)
        .order_by("order", "code", "id")
    )

    recent_lines = []
    if JournalLine is not None:
        try:
            recent_lines = (
                JournalLine.objects.select_related("entry", "account")
                .filter(account_id=acc.pk)
                .order_by("-created_at")[:30]
            )
        except Exception:
            recent_lines = []

    return render(
        request,
        "dashboard/accounting/account_detail.html",
        {
            "topbar_title": "Compte",
            "topbar_subtitle": f"{acc.code} — {acc.name}",
            "account": acc,
            "children": children,
            "recent_lines": recent_lines,
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Accounting"}, {"label": "Accounts"}, {"label": acc.code}],
        },
    )








# # dashboard/views/accounting/accounts.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.shortcuts import get_object_or_404, render

# from accounting.models.account import Account


# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)

# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def accounts_list_view(request):
#     q = (request.GET.get("q") or "").strip()
#     pole = (request.GET.get("pole") or "").strip().upper()
#     company = (request.GET.get("company") or "").strip().upper()
#     typ = (request.GET.get("type") or "").strip().upper()
#     subtype = (request.GET.get("subtype") or "").strip()
#     active = (request.GET.get("active") or "").strip()  # "1" / "0" / ""

#     qs = Account.objects.select_related("parent").all()

#     if pole:
#         qs = qs.filter(pole=pole)
#     if company:
#         qs = qs.filter(company_code=company)
#     if typ:
#         qs = qs.filter(type=typ)
#     if subtype:
#         qs = qs.filter(subtype=subtype)

#     if active == "1":
#         qs = qs.filter(is_active=True)
#     elif active == "0":
#         qs = qs.filter(is_active=False)

#     if q:
#         qs = qs.filter(
#             Q(code__icontains=q)
#             | Q(name__icontains=q)
#             | Q(account_number__icontains=q)
#             | Q(description__icontains=q)
#         )

#     qs = qs.order_by("pole", "company_code", "order", "code", "id")

#     paginator = Paginator(qs, 30)
#     page_obj = paginator.get_page(request.GET.get("page") or 1)

#     ctx = {
#         "q": q,
#         "pole": pole,
#         "company": company,
#         "type": typ,
#         "subtype": subtype,
#         "active": active,
#         "page_obj": page_obj,
#         "accounts": page_obj.object_list,
#         "paginator": paginator,
#         "type_choices": Account.Type.choices,
#         "subtype_choices": Account.Subtype.choices,
#         "pole_choices": getattr(Account, "Pole", None).choices if hasattr(Account, "Pole") else [],
#     }
#     return render(request, "dashboard/accounting/accounts_list.html", ctx)


# @login_required
# @permission_required("accounting.view_account", raise_exception=True)
# def account_detail_view(request, pk: int):
#     acc = get_object_or_404(Account.objects.select_related("parent"), pk=pk)
#     ctx = {"account": acc}
#     return render(request, "dashboard/accounting/account_detail.html", ctx)
