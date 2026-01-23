# dashboard/views/b2b/users.py
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_b2b_manager
from economic.b2b.models import CompanyUser
from dashboard.forms.b2b.company_user_form import CompanyUserForm


def _get_company_or_403(user):
    """
    Récupère la company du user de manière safe.
    Suppose un lien user -> company_user -> company.
    """
    company_user = getattr(user, "company_user", None)
    company = getattr(company_user, "company", None)
    if not company:
        raise PermissionDenied(_("Aucune entreprise associée à ce compte."))
    return company


@login_required
def b2b_users_list_view(request):
    if not is_b2b_manager(request.user):
        raise PermissionDenied

    company = _get_company_or_403(request.user)

    q = (request.GET.get("q") or "").strip()
    page_number = (request.GET.get("page") or "1").strip()

    qs = CompanyUser.objects.filter(company=company).select_related("user").order_by("-id")

    if q:
        qs = qs.filter(
            Q(user__email__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
        )

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/b2b/users_list.html", {
        "page_title": _("Utilisateurs entreprise"),
        "company": company,
        "q": q,
        "users": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    })


@login_required
def b2b_user_create_view(request):
    if not is_b2b_manager(request.user):
        raise PermissionDenied

    company = _get_company_or_403(request.user)

    form = CompanyUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        company_user = form.save(commit=False)
        company_user.company = company
        company_user.save()
        return redirect("dashboard:b2b:users")  # adapte si ton url name diffère

    return render(request, "dashboard/b2b/user_form.html", {
        "page_title": _("Ajouter un utilisateur"),
        "title": _("Ajouter un utilisateur"),
        "company": company,
        "form": form,
    })


@login_required
def b2b_user_update_view(request, pk: int):
    if not is_b2b_manager(request.user):
        raise PermissionDenied

    company = _get_company_or_403(request.user)

    company_user = get_object_or_404(CompanyUser, pk=pk, company=company)

    form = CompanyUserForm(request.POST or None, instance=company_user)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        updated.company = company  # sécurité serveur
        updated.save()
        return redirect("dashboard:b2b:users")  # adapte si ton url name diffère

    return render(request, "dashboard/b2b/user_form.html", {
        "page_title": _("Modifier l’utilisateur"),
        "title": _("Modifier l’utilisateur"),
        "company": company,
        "form": form,
        "obj": company_user,
    })





# # dashboard/views/b2b/users.py

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from dashboard.permissions import is_b2b_manager

# from economic.b2b.models import CompanyUser
# from dashboard.forms.b2b.company_user_form import CompanyUserForm


# @login_required
# def b2b_users(request):
#     users = CompanyUser.objects.filter(company=request.user.company_user.company)
#     return render(request, "dashboard/b2b/users.html", {"users": users})

# @login_required
# def b2b_users_list_view(request):
#     if not is_b2b_manager(request.user):
#         return render(request, "dashboard/errors/not_authorized.html", status=403)

#     company = request.user.company_user.company
#     users = CompanyUser.objects.filter(company=company)

#     return render(request, "dashboard/b2b/users_list.html", {
#         "company": company,
#         "users": users,
#     })


# @login_required
# def b2b_user_create_view(request):
#     if not is_b2b_manager(request.user):
#         return render(request, "dashboard/errors/not_authorized.html", status=403)

#     company = request.user.company_user.company
#     form = CompanyUserForm(request.POST or None)

#     if form.is_valid():
#         company_user = form.save(commit=False)
#         company_user.company = company
#         company_user.save()
#         return redirect("dashboard:b2b:users")

#     return render(request, "dashboard/b2b/user_form.html", {
#         "form": form,
#         "title": "Ajouter un utilisateur",
#     })


# @login_required
# def b2b_user_update_view(request, pk):
#     if not is_b2b_manager(request.user):
#         return render(request, "dashboard/errors/not_authorized.html", status=403)

#     company = request.user.company_user.company
#     company_user = get_object_or_404(
#         CompanyUser,
#         pk=pk,
#         company=company,
#     )

#     form = CompanyUserForm(request.POST or None, instance=company_user)

#     if form.is_valid():
#         form.save()
#         return redirect("dashboard:b2b:users")

#     return render(request, "dashboard/b2b/user_form.html", {
#         "form": form,
#         "title": "Modifier l’utilisateur",
#     })
