# dashboard/views/profile.py
from __future__ import annotations

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import breadcrumb, get_user_profile


# =====================================================
# Helpers
# =====================================================
def _model_has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return False


def _pick_user_fields(UserModel) -> tuple[str, ...]:
    """
    Sélectionne uniquement des champs existants sur CustomUser
    pour éviter FieldError.
    """
    candidates = ["first_name", "last_name", "full_name", "name", "username", "email"]
    fields = [f for f in candidates if _model_has_field(UserModel, f)]

    if not fields:
        # fallback minimal
        if _model_has_field(UserModel, "email"):
            return ("email",)
        if _model_has_field(UserModel, "username"):
            return ("username",)
        return tuple()

    return tuple(fields[:4])


def _build_user_form():
    """
    Construit un ModelForm User de manière dynamique.
    """
    UserModel = get_user_model()
    picked_fields = _pick_user_fields(UserModel)

    Meta = type("Meta", (), {"model": UserModel, "fields": picked_fields})
    UserUpdateForm = type("UserUpdateForm", (forms.ModelForm,), {"Meta": Meta})
    return UserUpdateForm


def _get_dashboard_profile(user):
    """
    Priorité:
    1) economic_profile (ancienne structure)
    2) profile/social_profile via helper
    """
    if hasattr(user, "economic_profile") and user.economic_profile:
        return user.economic_profile
    return get_user_profile(user)


def _build_profile_form(profile):
    """
    Fallback dynamique si ProfileUpdateForm n'existe pas.
    """
    fields = []
    for f in ("phone_number", "country", "address", "city", "avatar", "photo"):
        if hasattr(profile, f):
            fields.append(f)

    # Si aucun champ, on fabrique un form vide mais valide
    Meta = type("Meta", (), {"model": profile.__class__, "fields": tuple(fields)})
    ProfileUpdateDynamicForm = type("ProfileUpdateDynamicForm", (forms.ModelForm,), {"Meta": Meta})
    return ProfileUpdateDynamicForm


# =====================================================
# Views
# =====================================================
@login_required
def dashboard_profile_view(request):
    profile = _get_dashboard_profile(request.user)
    if not profile:
        messages.error(request, _("Aucun profil associé à ce compte."))
        return redirect("dashboard:router")

    return render(
        request,
        "dashboard/profile/profile.html",
        {
            "breadcrumbs": breadcrumb((_("Dashboard"), "/dashboard/"), (_("Profil"), None)),
            "profile": profile,
        },
    )


@login_required
def dashboard_profile_edit_view(request):
    profile = _get_dashboard_profile(request.user)
    if not profile:
        messages.error(request, _("Aucun profil associé à ce compte."))
        return redirect("dashboard:router")

    # 1) User form (adaptatif)
    UserForm = _build_user_form()
    user_form = UserForm(request.POST or None, instance=request.user)

    # 2) Profile form (priorité au form existant)
    try:
        from dashboard.forms.profile_form import ProfileUpdateForm
        ProfileForm = ProfileUpdateForm
    except Exception:
        ProfileForm = _build_profile_form(profile)

    profile_form = ProfileForm(
        request.POST or None,
        request.FILES,
        instance=profile,
    )

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _("Profil mis à jour avec succès."))
            return redirect("dashboard:profile")
        messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

    return render(
        request,
        "dashboard/profile/profile_edit.html",
        {
            "breadcrumbs": breadcrumb(
                (_("Dashboard"), "/dashboard/"),
                (_("Profil"), "/dashboard/profile/"),
                (_("Modifier"), None),
            ),
            "profile": profile,
            "user_form": user_form,
            "form": profile_form,
            "title": _("Modifier le profil"),
        },
    )




# # dashboard/views/profile.py
# from __future__ import annotations

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, get_user_profile


# # =====================================================
# # Helpers
# # =====================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     """
#     Sélectionne uniquement des champs existants sur CustomUser
#     pour éviter FieldError.
#     """
#     candidates = ["first_name", "last_name", "full_name", "name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]

#     if not fields:
#         if _model_has_field(UserModel, "email"):
#             return ("email",)
#         if _model_has_field(UserModel, "username"):
#             return ("username",)
#         return tuple()

#     # Limite pour éviter des forms trop longs
#     return tuple(fields[:4])


# def _build_user_form():
#     """
#     Construit un ModelForm User de manière dynamique (Meta dynamique),
#     corrige le problème de scope: class Meta: fields = fields
#     """
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     Meta = type("Meta", (), {"model": UserModel, "fields": picked_fields})
#     UserUpdateForm = type("UserUpdateForm", (forms.ModelForm,), {"Meta": Meta})
#     return UserUpdateForm


# def _get_dashboard_profile(user):
#     """
#     Priorité:
#     1) economic_profile (ton ancienne structure)
#     2) profile / social_profile via helper
#     """
#     if hasattr(user, "economic_profile") and user.economic_profile:
#         return user.economic_profile
#     return get_user_profile(user)


# def _build_profile_form(profile):
#     """
#     Fallback dynamique si ProfileUpdateForm n'existe pas.
#     """
#     fields = []
#     for f in ("phone_number", "country", "address", "city", "avatar", "photo"):
#         if hasattr(profile, f):
#             fields.append(f)

#     Meta = type("Meta", (), {"model": profile.__class__, "fields": tuple(fields)})
#     ProfileUpdateDynamicForm = type("ProfileUpdateDynamicForm", (forms.ModelForm,), {"Meta": Meta})
#     return ProfileUpdateDynamicForm


# # =====================================================
# # Views
# # =====================================================
# @login_required
# def dashboard_profile_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Profil"), None)),
#             "profile": profile,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     # 1) User form (adaptatif)
#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 2) Profile form (priorité à ton form existant)
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), "/dashboard/"),
#                 (_("Profil"), "/dashboard/profile/"),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "user_form": user_form,  # optionnel dans template
#             "form": profile_form,    # ton template utilise souvent "form"
#             "title": _("Modifier le profil"),
#         },
#     )







# # dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _

# from dashboard.forms.profile_form import ProfileUpdateForm


# @login_required
# def dashboard_profile_view(request):
#     """Page d'affichage du profil (économique)."""
#     profile = getattr(request.user, "economic_profile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")  # ✅ existe

#     return render(request, "dashboard/profile/profile.html", {"profile": profile})


# @login_required
# def dashboard_profile_edit_view(request):
#     """Page d'édition du profil (économique)."""
#     profile = getattr(request.user, "economic_profile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")  # ✅ existe

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")  # ✅ route profile
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {"form": form, "profile": profile},
#     )






# # ✅ dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from dashboard.forms.profile_form import ProfileUpdateForm
# from django.utils.translation import gettext_lazy as _


# @login_required
# def dashboard_profile_view(request):
#     """ Page d'affichage du profil """
#     profile = getattr(request.user, "userprofile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")

#     context = {"profile": profile}
#     return render(request, "dashboard/profile/profile.html", context)


# @login_required
# def dashboard_profile_edit_view(request):
#     """ Page d'édition du profil """
#     profile = getattr(request.user, "userprofile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     return render(request, "dashboard/profile/profile_edit.html", {"form": form, "profile": profile})






# # ✅ dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from dashboard.forms.profile_form import ProfileUpdateForm
# from django.utils.translation import gettext_lazy as _

# @login_required
# def dashboard_profile_view(request):
#     profile = getattr(request.user, "userprofile", None)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")  # Ou une vue d’accueil

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     context = {"form": form}
#     return render(request, "dashboard/profile/profile.html", context)



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def dashboard_profile_view(request):
#     return render(request, "dashboard/profile.html")




