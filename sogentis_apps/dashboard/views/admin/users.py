# dashboard/views/admin/users.py
from __future__ import annotations

from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, FieldDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user

User = get_user_model()


def _is_staff_or_admin(user) -> bool:
    return bool(is_admin(user) or is_staff_user(user))


def _model_has_field(model, field: str) -> bool:
    try:
        model._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False
    except Exception:
        return False


def _safe_ordering_field(model) -> str:
    return "date_joined" if _model_has_field(model, "date_joined") else "id"


def _build_search_q(model, q: str) -> Q:
    parts: List[Q] = []
    if _model_has_field(model, "email"):
        parts.append(Q(email__icontains=q))
    if _model_has_field(model, "username"):
        parts.append(Q(username__icontains=q))
    if _model_has_field(model, "first_name"):
        parts.append(Q(first_name__icontains=q))
    if _model_has_field(model, "last_name"):
        parts.append(Q(last_name__icontains=q))

    if not parts:
        return Q()

    query = parts[0]
    for p in parts[1:]:
        query |= p
    return query


@login_required
def admin_users_list_view(request):
    """
    Admin: liste utilisateurs (prod).
    - Recherche via ?q=
    - Pagination via ?page=
    Template: dashboard/admin/users_list.html
    """
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    q = (request.GET.get("q") or "").strip()
    page_number = (request.GET.get("page") or "1").strip()

    ordering_field = _safe_ordering_field(User)
    qs = User.objects.all().order_by(f"-{ordering_field}")

    # perf: limiter les colonnes si possible (safe)
    only_fields = ["id"]
    for f in ("username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"):
        if _model_has_field(User, f):
            only_fields.append(f)
    if _model_has_field(User, ordering_field):
        only_fields.append(ordering_field)

    try:
        qs = qs.only(*only_fields)
    except Exception:
        pass

    if q:
        qs = qs.filter(_build_search_q(User, q))

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_title": _("Utilisateurs"),
        "q": q,
        "users": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    }
    return render(request, "dashboard/admin/users_list.html", context)





# # dashboard/views/admin/users.py 
# from __future__ import annotations

# from typing import List

# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied, FieldDoesNotExist
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# User = get_user_model()


# def _is_staff_or_admin(user) -> bool:
#     return bool(is_admin(user) or is_staff_user(user))


# def _model_has_field(model, field: str) -> bool:
#     try:
#         model._meta.get_field(field)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# def _safe_ordering_field(model) -> str:
#     # ordre par date_joined si dispo, sinon par id
#     return "date_joined" if _model_has_field(model, "date_joined") else "id"


# def _build_search_q(model, q: str) -> Q:
#     """
#     Construit un Q object uniquement avec les champs existants.
#     """
#     parts: List[Q] = []
#     if _model_has_field(model, "email"):
#         parts.append(Q(email__icontains=q))
#     if _model_has_field(model, "username"):
#         parts.append(Q(username__icontains=q))
#     if _model_has_field(model, "first_name"):
#         parts.append(Q(first_name__icontains=q))
#     if _model_has_field(model, "last_name"):
#         parts.append(Q(last_name__icontains=q))

#     # fallback minimal si rien n'existe (rare)
#     if not parts:
#         return Q()

#     query = parts[0]
#     for p in parts[1:]:
#         query |= p
#     return query


# @login_required
# def admin_users_list_view(request):
#     """
#     Admin: liste utilisateurs (prod).
#     - Recherche via ?q=
#     - Pagination via ?page=
#     - Rend: templates/dashboard/admin/users.html
#     """
#     if not _is_staff_or_admin(request.user):
#         raise PermissionDenied

#     q = (request.GET.get("q") or "").strip()
#     page = (request.GET.get("page") or "1").strip()

#     ordering_field = _safe_ordering_field(User)
#     qs = User.objects.all().order_by(f"-{ordering_field}")

#     # perf: limiter les colonnes si elles existent
#     only_fields = ["id"]
#     for f in ("username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"):
#         if _model_has_field(User, f):
#             only_fields.append(f)
#     if _model_has_field(User, ordering_field):
#         only_fields.append(ordering_field)

#     try:
#         qs = qs.only(*only_fields)
#     except Exception:
#         # si backend / custom user ne supporte pas cleanly
#         pass

#     if q:
#         qs = qs.filter(_build_search_q(User, q))

#     paginator = Paginator(qs, 25)  # 25 users/page
#     page_obj = paginator.get_page(page)

#     context = {
#         "page_title": _("Utilisateurs"),
#         "q": q,
#         "users": page_obj.object_list,  # utilisé par users_list.html
#         "page_obj": page_obj,
#         "paginator": paginator,
#         "is_paginated": page_obj.has_other_pages(),
#     }
#     return render(request, "dashboard/admin/users.html", context)






# # dashboard/views/admin/users.py
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import get_user_model
# from django.core.exceptions import PermissionDenied
# from django.db.models import Q
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# User = get_user_model()


# def _is_staff_or_admin(user):
#     return is_admin(user) or is_staff_user(user)


# @login_required
# def admin_users_list_view(request):
#     """
#     Liste des utilisateurs pour l’admin.
#     - Recherche simple via ?q=
#     """
#     user = request.user
#     if not _is_staff_or_admin(user):
#         raise PermissionDenied

#     q = (request.GET.get("q") or "").strip()

#     users_qs = User.objects.all().order_by("-date_joined")

#     if q:
#         users_qs = users_qs.filter(
#             Q(email__icontains=q) |
#             Q(username__icontains=q) |
#             Q(first_name__icontains=q) |
#             Q(last_name__icontains=q)
#         )

#     context = {
#         "page_title": _("Utilisateurs"),
#         "users": users_qs,
#     }
#     return render(request, "dashboard/admin/users_list.html", context)





# # dashboard/views/admin/users.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.contrib.auth import get_user_model
# from dashboard.permissions import is_admin

# User = get_user_model()


# @login_required
# @user_passes_test(is_admin)
# def users_list(request):
#     users = User.objects.all().order_by("-date_joined")
#     return render(
#         request,
#         "dashboard/admin/users.html",
#         {"users": users},
#     )
