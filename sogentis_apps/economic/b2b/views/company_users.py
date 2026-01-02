# economic/b2b/views/company_users.py
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from economic.decorators import b2b_admin_required
from economic.b2b.forms.company_user_forms import (
    CompanyUserCreateForm,
    CompanyUserUpdateForm,
)
from economic.b2b.models import CompanyUser

User = get_user_model()


def _user_defaults_for_email(email: str) -> dict:
    """
    Création safe selon USERNAME_FIELD.
    - si USERNAME_FIELD != 'email', on le remplit avec l'email
    - ne casse pas un CustomUser sans champ username
    """
    defaults = {}
    username_field = getattr(User, "USERNAME_FIELD", "username")
    if username_field and username_field != "email":
        defaults[username_field] = email
    return defaults


@b2b_admin_required
def company_users_list_view(request):
    company = request.user.company_user.company
    users = CompanyUser.objects.select_related("user", "company").filter(company=company).order_by("-created_at")

    return render(
        request,
        "economic/b2b/company_users/list.html",
        {"company": company, "users": users},
    )


@b2b_admin_required
def company_user_add_view(request):
    company = request.user.company_user.company

    if request.method == "POST":
        form = CompanyUserCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            role = form.cleaned_data["role"]

            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults=_user_defaults_for_email(email),
                )

                # Si ton modèle user n'a pas email unique, on sécurise avec get_or_create ci-dessus
                # Vérif: un user ne peut pas déjà être lié à une autre entreprise (OneToOne)
                if hasattr(user, "company_user") and user.company_user and user.company_user.company_id != company.id:
                    messages.error(
                        request,
                        _("Cet utilisateur appartient déjà à une autre entreprise."),
                    )
                    return redirect("b2b:company_users")

                # Créer / mettre à jour l'appartenance
                CompanyUser.objects.update_or_create(
                    user=user,
                    defaults={
                        "company": company,
                        "role": role,
                        "is_active": True,
                    },
                )

            messages.success(request, _("Utilisateur ajouté à l’entreprise"))
            return redirect("b2b:company_users")
    else:
        form = CompanyUserCreateForm()

    return render(
        request,
        "economic/b2b/company_users/form.html",
        {"company": company, "form": form},
    )


@b2b_admin_required
def company_user_edit_view(request, pk: int):
    company = request.user.company_user.company

    company_user = get_object_or_404(
        CompanyUser.objects.select_related("user", "company"),
        pk=pk,
        company=company,
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
        "economic/b2b/company_users/form.html",
        {"company": company, "form": form, "company_user": company_user},
    )






# # /economic/b2b/views/company_users.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.utils.translation import gettext_lazy as _

# from economic.decorators import b2b_admin_required
# from economic.b2b.models import CompanyUser
# from economic.b2b.forms.company_user_forms import (
#     CompanyUserCreateForm,
#     CompanyUserUpdateForm,
# )

# User = get_user_model()


# @b2b_admin_required
# def company_users_list_view(request):
#     company = request.user.company_user.company
#     users = CompanyUser.objects.filter(company=company)

#     return render(
#         request,
#         "b2b/company_users/list.html",
#         {"users": users},
#     )


# # ===#
# # Ajouter un utilisateur #
# # === #

# @b2b_admin_required
# def company_user_add_view(request):
#     company = request.user.company_user.company

#     if request.method == "POST":
#         form = CompanyUserCreateForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data["email"]
#             role = form.cleaned_data["role"]

#             user, _ = User.objects.get_or_create(
#                 email=email,
#                 defaults={"username": email},
#             )

#             CompanyUser.objects.get_or_create(
#                 user=user,
#                 company=company,
#                 defaults={"role": role},
#             )

#             messages.success(request, _("Utilisateur ajouté à l’entreprise"))
#             return redirect("b2b:company_users")

#     else:
#         form = CompanyUserCreateForm()

#     return render(
#         request,
#         "b2b/company_users/form.html",
#         {"form": form},
#     )
# #===#
# # Modifier / désactiver#
# #===#

# @b2b_admin_required
# def company_user_edit_view(request, pk):
#     company_user = get_object_or_404(
#         CompanyUser,
#         pk=pk,
#         company=request.user.company_user.company,
#     )

#     if request.method == "POST":
#         form = CompanyUserUpdateForm(request.POST, instance=company_user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Utilisateur mis à jour"))
#             return redirect("b2b:company_users")
#     else:
#         form = CompanyUserUpdateForm(instance=company_user)

#     return render(
#         request,
#         "b2b/company_users/form.html",
#         {"form": form, "company_user": company_user},
#     )
