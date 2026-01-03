# dashboard/views/pending_profiles.py
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import has_field


def _get_profile_model():
    """
    Essaie d'importer ton modèle de profil "social" ou générique.
    Ajuste si ton modèle réel est ailleurs.
    """
    try:
        from accounts_users.models.social.social_profile import SocialProfile
        return SocialProfile
    except Exception:
        try:
            from accounts_users.models.users_profile import UserProfile
            return UserProfile
        except Exception:
            return None


@staff_member_required
def pending_profiles_list(request):
    Profile = _get_profile_model()
    if Profile is None:
        messages.error(request, _("Aucun modèle de profil trouvé (SocialProfile/UserProfile)."))
        return render(request, "dashboard/admin/pending_profiles_list.html", {"pending_profiles": []})

    qs = Profile.objects.all()

    # logique "pending" robuste selon champs existants
    if has_field(Profile, "status"):
        qs = qs.filter(status__in=["PENDING", "PENDING_VALIDATION", "WAITING", "EN_ATTENTE"])
    elif has_field(Profile, "is_active_member"):
        qs = qs.filter(is_active_member=False)
    elif has_field(Profile, "is_approved"):
        qs = qs.filter(is_approved=False)
    else:
        # pas de champ -> on ne devine pas, on affiche vide (pas fake)
        qs = Profile.objects.none()

    qs = qs.select_related("user").order_by("-created_at") if has_field(Profile, "created_at") else qs.select_related("user")

    return render(request, "dashboard/admin/pending_profiles_list.html", {
        "pending_profiles": qs,
        "breadcrumbs": [
            {"label": _("Dashboard"), "url": "/dashboard/"},
            {"label": _("Admin"), "url": "/dashboard/admin/"},
            {"label": _("Profils en attente"), "url": None},
        ],
    })


@staff_member_required
def validate_profile_view(request, profile_id):
    Profile = _get_profile_model()
    if Profile is None:
        messages.error(request, _("Aucun modèle de profil trouvé."))
        return redirect("dashboard:pending_profiles")

    profile = get_object_or_404(Profile, pk=profile_id)

    # champs possibles
    if has_field(Profile, "status"):
        profile.status = "APPROVED"
        profile.save(update_fields=["status"])
    elif has_field(Profile, "is_active_member"):
        profile.is_active_member = True
        profile.save(update_fields=["is_active_member"])
    elif has_field(Profile, "is_approved"):
        profile.is_approved = True
        profile.save(update_fields=["is_approved"])

    messages.success(request, _("Profil approuvé."))
    return redirect("dashboard:pending_profiles")


@staff_member_required
def refuse_profile_view(request, profile_id):
    Profile = _get_profile_model()
    if Profile is None:
        messages.error(request, _("Aucun modèle de profil trouvé."))
        return redirect("dashboard:pending_profiles")

    profile = get_object_or_404(Profile, pk=profile_id)

    if has_field(Profile, "status"):
        profile.status = "REFUSED"
        profile.save(update_fields=["status"])
    elif has_field(Profile, "is_active_member"):
        profile.is_active_member = False
        profile.save(update_fields=["is_active_member"])
    elif has_field(Profile, "is_approved"):
        profile.is_approved = False
        profile.save(update_fields=["is_approved"])

    messages.warning(request, _("Profil refusé."))
    return redirect("dashboard:pending_profiles")





# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings

# from accounts_users.models.users_economic_profile import UserEconomicProfile


# # ======================================================
# # LISTE DES PROFILS EN ATTENTE
# # ======================================================
# @staff_member_required
# def pending_profiles_list(request):
#     profiles = UserEconomicProfile.objects.filter(status=UserEconomicProfile.Status.PENDING)
#     return render(request, "dashboard/profile/pending_list.html", {"profiles": profiles})


# # ======================================================
# # APPROBATION PROFIL
# # ======================================================
# @staff_member_required
# def validate_profile_view(request, profile_id):
#     profile = get_object_or_404(UserEconomicProfile, id=profile_id)
#     user = profile.user

#     profile.status = UserEconomicProfile.Status.APPROVED
#     profile.save(update_fields=["status", "updated_at"])

#     subject = _("Validation de votre profil SOGENTIS")
#     html_message = render_to_string("accounts_users/emails/profile_approved.html", {"user": user, "profile": profile})

#     send_mail(
#         subject=subject,
#         message=_("Votre profil a été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#         fail_silently=True,  # évite de casser l'admin si SMTP down
#     )

#     messages.success(request, _("Le profil a été validé et un e-mail a été envoyé."))
#     return redirect("dashboard:pending_profiles")


# # ======================================================
# # REFUS PROFIL
# # ======================================================
# @staff_member_required
# def refuse_profile_view(request, profile_id):
#     profile = get_object_or_404(UserEconomicProfile, id=profile_id)
#     user = profile.user

#     profile.status = UserEconomicProfile.Status.REFUSED
#     profile.save(update_fields=["status", "updated_at"])

#     subject = _("Votre profil SOGENTIS a été refusé")
#     html_message = render_to_string("accounts_users/emails/profile_refused.html", {"user": user, "profile": profile})

#     send_mail(
#         subject=subject,
#         message=_("Votre profil n’a pas été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#         fail_silently=True,
#     )

#     messages.error(request, _("Le profil a été refusé et un e-mail a été envoyé."))
#     return redirect("dashboard:pending_profiles")








# # dashboard/views/pending_profiles.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings

# from accounts_users.models.users_economic_profile import UserProfile


# # ======================================================
# # LISTE DES PROFILS EN ATTENTE
# # ======================================================
# # @staff_member_required
# def pending_profiles_list(request):
#     profiles = UserProfile.objects.filter(status="pending")
#     return render(request, "dashboard/profile/pending_list.html", {
#         "profiles": profiles
#     })


# # ======================================================
# # APPROBATION PROFIL
# # ======================================================
# # @staff_member_required
# def validate_profile_view(request, profile_id):
#     profile = get_object_or_404(UserProfile, id=profile_id)
#     user = profile.user

#     # 1. mise à jour statut
#     profile.status = "approved"
#     profile.save()

#     # 2. envoi email
#     subject = _("Validation de votre profil SOGENTIS")
#     html_message = render_to_string(
#         "accounts_users/emails/profile_approved.html",
#         {"user": user}
#     )

#     send_mail(
#         subject=subject,
#         message=_("Votre profil a été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#     )

#     # 3. message interface
#     messages.success(request, _("Le profil a été validé et un e-mail a été envoyé."))

#     return redirect("dashboard:pending_profiles")


# # ======================================================
# # REFUS PROFIL
# # ======================================================
# # @staff_member_required
# def refuse_profile_view(request, profile_id):
#     profile = get_object_or_404(UserProfile, id=profile_id)
#     user = profile.user

#     # 1. mise à jour statut
#     profile.status = "refused"
#     profile.save()

#     # 2. envoi email
#     subject = _("Votre profil SOGENTIS a été refusé")
#     html_message = render_to_string(
#         "accounts_users/emails/profile_refused.html",
#         {"user": user}
#     )

#     send_mail(
#         subject=subject,
#         message=_("Votre profil n’a pas été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#     )

#     # 3. message interface
#     messages.error(request, _("Le profil a été refusé et un e-mail a été envoyé."))

#     return redirect("dashboard:pending_profiles")
