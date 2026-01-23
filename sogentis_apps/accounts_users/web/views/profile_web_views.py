# accounts_users/web/views/profile_web_views.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

from accounts_users.forms.user_forms import UserEmailUpdateForm


# ============================================================
# Helpers profil (central -> social -> economic)
# ============================================================
def _get_best_profile(user):
    # 1) profil central
    profile = getattr(user, "userprofile", None)
    if profile is not None:
        return profile, "userprofile"

    # 2) social
    try:
        from accounts_users.models.social.social_profile import SocialProfile
        sp = SocialProfile.objects.filter(user=user).first()
        if sp:
            return sp, "social"
    except Exception:
        pass

    # 3) economic
    try:
        from accounts_users.models.users_economic_profile import UserEconomicProfile
        ep = UserEconomicProfile.objects.filter(user=user).first()
        if ep:
            return ep, "economic"
    except Exception:
        pass

    return None, None


def _get_profile_form_class(profile_kind: str):
    """
    Renvoie un ModelForm adapté au type de profil.
    """
    if profile_kind == "userprofile":
        # Si tu as un vrai UserProfileForm, utilise-le ici.
        # Sinon fallback dynamique dans update_profile_logic()
        return None

    if profile_kind == "social":
        try:
            # NOTE: SocialRegistrationForm contient terms/phone_number => OK en édition
            from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
            return SocialRegistrationForm
        except Exception:
            return None

    if profile_kind == "economic":
        try:
            from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
            return UserProfileEconomicForm
        except Exception:
            return None

    return None


def _build_dynamic_modelform(model_cls):
    from django import forms

    class DynamicProfileForm(forms.ModelForm):
        class Meta:
            model = model_cls
            exclude = ("user",)

    return DynamicProfileForm


# ============================================================
# 1) LOGIQUE PURE (remplace ton update_profile_logic cassé)
# ============================================================
def update_profile_logic(request):
    """
    Logique pure de mise à jour du profil.
    Retourne (profile_form, email_form, profile, profile_kind, state)

    state:
      True  -> ok
      False -> POST invalide
      None  -> GET initial
    """
    user = request.user
    profile, profile_kind = _get_best_profile(user)

    if profile is None:
        # pas de profil => on ne crash pas
        return None, None, None, None, False

    ProfileForm = _get_profile_form_class(profile_kind)
    if ProfileForm is None:
        ProfileForm = _build_dynamic_modelform(profile.__class__)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        email_form = UserEmailUpdateForm(request.POST, instance=user)

        ok_profile = profile_form.is_valid()
        ok_email = email_form.is_valid()

        if ok_profile and ok_email:
            # certains forms (economic) ont save(user=...)
            try:
                profile_form.save(user=user)
            except TypeError:
                profile_form.save()

            email_form.save()
            return profile_form, email_form, profile, profile_kind, True

        return profile_form, email_form, profile, profile_kind, False

    # GET
    profile_form = ProfileForm(instance=profile)
    email_form = UserEmailUpdateForm(instance=user)
    return profile_form, email_form, profile, profile_kind, None


# ============================================================
# 2) VUE UTILISATEUR : Modifier son profil
# ============================================================
@login_required
def profile_edit_view(request):
    profile_form, email_form, profile, profile_kind, state = update_profile_logic(request)

    if state is True:
        messages.success(request, _("Votre profil a été mis à jour avec succès."))
        # ✅ cohérent avec ton namespace actuel
        return redirect("accounts_users:web:profile:profile")

    if state is False and profile is not None:
        messages.error(request, _("Veuillez corriger les erreurs."))

    if profile is None:
        messages.error(request, _("Profil introuvable."))
        return redirect("dashboard:hub")

    return render(
        request,
        "dashboard/profile/profile_edit.html",
        {
            "profile_form": profile_form,
            "email_form": email_form,
            "profile": profile,
            "profile_kind": profile_kind,
        },
    )


# ============================================================
# 3) VUE ADMIN : liste des profils économiques en attente
# ============================================================
@staff_member_required
def list_pending_profiles(request):
    from accounts_users.models.users_economic_profile import UserEconomicProfile

    # ⚠️ adapte le filtre selon ton modèle (status / validation_status)
    qs = UserEconomicProfile.objects.all()
    if hasattr(UserEconomicProfile, "validation_status"):
        qs = qs.filter(validation_status="PENDING")
    elif hasattr(UserEconomicProfile, "status"):
        qs = qs.filter(status="pending")

    return render(
        request,
        "accounts_users/profiles/pending_list.html",
        {"profiles": qs},
    )


# ============================================================
# 4) VUE UTILISATEUR : Notification “profil en attente”
# ============================================================
@login_required
def profile_pending_notice(request):
    return render(request, "accounts_users/registration/profile_pending_notice.html")





# # accounts_users/web/views/profile_web_views.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpRequest
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.user_forms import UserEmailUpdateForm


# # ============================================================
# # Helpers : détecter le bon "profil"
# # ============================================================
# def _get_profile_instance(user):
#     """
#     Retourne l'instance profil la plus pertinente existante.
#     Ordre :
#     1) user.userprofile (si modèle central existe)
#     2) SocialProfile (si existe)
#     3) UserEconomicProfile (si existe)
#     Sinon None.
#     """
#     # 1) UserProfile central
#     profile = getattr(user, "userprofile", None)
#     if profile is not None:
#         return profile

#     # 2) SocialProfile
#     try:
#         from accounts_users.models.social.social_profile import SocialProfile
#         sp = SocialProfile.objects.filter(user=user).first()
#         if sp:
#             return sp
#     except Exception:
#         pass

#     # 3) Economic profile
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile
#         ep = UserEconomicProfile.objects.filter(user=user).first()
#         if ep:
#             return ep
#     except Exception:
#         pass

#     return None


# def _get_profile_form_class(profile_instance):
#     """
#     Retourne le ModelForm adapté au type de profil.
#     """
#     if profile_instance is None:
#         return None

#     # UserProfile central (si tu as un form dédié)
#     if profile_instance.__class__.__name__.lower() == "userprofile":
#         try:
#             from accounts_users.forms.profile_forms import UserProfileForm  # si tu l’as
#             return UserProfileForm
#         except Exception:
#             # fallback minimal : si tu n'as pas UserProfileForm,
#             # on utilisera un ModelForm dynamique (ci-dessous)
#             return None

#     # SocialProfile
#     if profile_instance.__class__.__name__.lower() == "socialprofile":
#         try:
#             from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
#             # Attention: SocialRegistrationForm contient terms/phone_number -> ok en edition
#             return SocialRegistrationForm
#         except Exception:
#             return None

#     # UserEconomicProfile
#     if profile_instance.__class__.__name__.lower() == "usereconomicprofile":
#         try:
#             from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
#             return UserProfileEconomicForm
#         except Exception:
#             return None

#     return None


# def _build_dynamic_modelform(model_cls):
#     """
#     Fallback safe si tu n'as pas de form dédié.
#     -> ne casse pas le site.
#     """
#     from django import forms

#     class DynamicProfileForm(forms.ModelForm):
#         class Meta:
#             model = model_cls
#             exclude = ("user",)

#     return DynamicProfileForm


# # ============================================================
# # Vue
# # ============================================================
# @login_required
# def profile_edit_view(request: HttpRequest):
#     user = request.user
#     profile = _get_profile_instance(user)

#     if profile is None:
#         messages.error(request, _("Profil introuvable."))
#         return redirect("dashboard:hub")

#     ProfileForm = _get_profile_form_class(profile)
#     if ProfileForm is None:
#         ProfileForm = _build_dynamic_modelform(profile.__class__)

#     if request.method == "POST":
#         profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
#         email_form = UserEmailUpdateForm(request.POST, instance=user)

#         if profile_form.is_valid() and email_form.is_valid():
#             # certains forms ont un save(user=...) (ex: UserProfileEconomicForm)
#             try:
#                 profile_form.save(user=user)
#             except TypeError:
#                 profile_form.save()

#             email_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("accounts_users:web:profile:profile")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     else:
#         profile_form = ProfileForm(instance=profile)
#         email_form = UserEmailUpdateForm(instance=user)

#     return render(
#         request,
#         "accounts_users/profile/profile_edit.html",
#         {
#             "profile_form": profile_form,
#             "email_form": email_form,
#             "profile_kind": profile.__class__.__name__,
#         },
#     )







# # accounts_users/web/views/profile_web_views.py

# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_economic_profile import UserEconomicProfile
# from accounts_users.views.profiles import update_profile_logic


# # ==========================================================
# # 1. VUE UTILISATEUR : Modifier son propre profil
# # ==========================================================
# @login_required
# def profile_edit_view(request):
#     """
#     Vue utilisateur pour modifier SON propre profil.
#     - Appelle la logique métier pure update_profile_logic()
#     - Affiche messages de succès/erreur
#     - Rend le template du dashboard (logique, cohérent)
#     """
#     form, success = update_profile_logic(request)

#     if success is True:
#         messages.success(request, _("Votre profil a été mis à jour avec succès."))
#         return redirect("dashboard:profile")  # la bonne URL dashboard

#     elif success is False:
#         messages.error(request, _("Veuillez corriger les erreurs."))

#     return render(request, "dashboard/profile/profile_edit.html", {
#         "form": form,
#         "profile": request.user.userprofile,
#     })


# # ==========================================================
# # 2. VUE ADMIN : liste des profils en attente
# # ==========================================================
# @staff_member_required
# def list_pending_profiles(request):
#     """
#     Liste les profils utilisateurs encore en état 'pending'.
#     Réservé aux administrateurs.
#     """
#     profiles = UserEconomicProfile.objects.filter(status="pending")

#     return render(request, "accounts_users/profiles/pending_list.html", {
#         "profiles": profiles
#     })


# # ==========================================================
# # 3. VUE UTILISATEUR : Notification “profil en attente”
# # ==========================================================
# @login_required
# def profile_pending_notice(request):
#     """
#     Affiche un écran d'avertissement au user dont le profil
#     n’est pas encore validé/activé dans le système interne.
#     """
#     return render(
#         request,
#         "accounts_users/registration/profile_pending_notice.html"
#     )









# # accounts_users/web/views/profile_web_views.py
# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.views.profiles import update_profile_logic


# # ==========================================================
# # 1. VUE USER : Modifier son propre profil
# # ==========================================================
# @login_required
# def profile_edit_view(request):
#     """
#     Vue complète : rend le template, affiche les messages.
#     """
#     form, success = update_profile_logic(request)

#     if success is True:
#         messages.success(request, _("Votre profil a été mis à jour avec succès."))
#         return redirect("dashboard:profile")
#     elif success is False:
#         messages.error(request, _("Veuillez corriger les erreurs."))

#     return render(request, "accounts_users/registration/profile_edit.html", {
#         "form": form,
#         "profile": request.user.userprofile,
#     })


# # ==========================================================
# # 2. VUE ADMIN : liste des profils en attente
# # ==========================================================
# @staff_member_required
# def list_pending_profiles(request):
#     profiles = UserProfile.objects.filter(status="pending")
#     return render(request, "accounts_users/profiles/pending_list.html", {
#         "profiles": profiles
#     })


# # ==========================================================
# # 3. VUE USER : Notification “profil en attente”
# # ==========================================================
# @login_required
# def profile_pending_notice(request):
#     return render(request, "accounts_users/registration/profile_pending_notice.html")





# # accounts_users/web/views/profile_views.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from accounts_users.models.users_profile import UserProfile

# @staff_member_required
# def list_pending_profiles(request):
#     """
#     Vue admin : liste les profils utilisateur en attente de validation.
#     """
#     profiles = UserProfile.objects.filter(status='pending')
#     return render(request, 'accounts_users/profiles/pending_list.html', {'profiles': profiles})

# @login_required
# def profile_pending_notice(request):
#     """
#     Affiche un message au user dont le profil est en attente de validation.
#     """
#     return render(request, "accounts_users/registration/profile_pending_notice.html")





# # accounts_users/web/views/profile_views.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from accounts_users.models.users_profile import UserProfile

# @staff_member_required
# def list_pending_profiles(request):
#     profiles = UserProfile.objects.filter(status='pending')
#     return render(request, 'accounts_users/profiles/pending_list.html', {'profiles': profiles})

# @login_required
# def profile_pending_notice(request):
#     return render(request, "accounts_users/registration/profile_pending_notice.html")

