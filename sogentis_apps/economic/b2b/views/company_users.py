from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from economic.decorators import b2b_admin_required
from economic.b2b.models import CompanyUser
from economic.b2b.forms.company_user_forms import (
    CompanyUserCreateForm,
    CompanyUserUpdateForm,
)

User = get_user_model()


@b2b_admin_required
def company_users_list_view(request):
    company = request.user.company_user.company
    users = CompanyUser.objects.filter(company=company)

    return render(
        request,
        "b2b/company_users/list.html",
        {"users": users},
    )


# ===#
# Ajouter un utilisateur #
# === #

@b2b_admin_required
def company_user_add_view(request):
    company = request.user.company_user.company

    if request.method == "POST":
        form = CompanyUserCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            role = form.cleaned_data["role"]

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"username": email},
            )

            CompanyUser.objects.get_or_create(
                user=user,
                company=company,
                defaults={"role": role},
            )

            messages.success(request, _("Utilisateur ajouté à l’entreprise"))
            return redirect("b2b:company_users")

    else:
        form = CompanyUserCreateForm()

    return render(
        request,
        "b2b/company_users/form.html",
        {"form": form},
    )
#===#
# Modifier / désactiver#
#===#

@b2b_admin_required
def company_user_edit_view(request, pk):
    company_user = get_object_or_404(
        CompanyUser,
        pk=pk,
        company=request.user.company_user.company,
    )

    if request.method == "POST":
        form = CompanyUserUpdateForm(request.POST, instance=company_user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Utilisateur mis à jour"))
            return redirect("b2b:company_users")
    else:
        form = CompanyUserUpdateForm(instance=company_user)

    return render(
        request,
        "b2b/company_users/form.html",
        {"form": form, "company_user": company_user},
    )
