from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from accounts_users.models.users_economic_profile import UserEconomicProfile


# ======================================================
# LISTE DES PROFILS EN ATTENTE
# ======================================================
@staff_member_required
def pending_profiles_list(request):
    profiles = UserEconomicProfile.objects.filter(status=UserEconomicProfile.Status.PENDING)
    return render(request, "dashboard/profile/pending_list.html", {"profiles": profiles})


# ======================================================
# APPROBATION PROFIL
# ======================================================
@staff_member_required
def validate_profile_view(request, profile_id):
    profile = get_object_or_404(UserEconomicProfile, id=profile_id)
    user = profile.user

    profile.status = UserEconomicProfile.Status.APPROVED
    profile.save(update_fields=["status", "updated_at"])

    subject = _("Validation de votre profil SOGENTIS")
    html_message = render_to_string("accounts_users/emails/profile_approved.html", {"user": user, "profile": profile})

    send_mail(
        subject=subject,
        message=_("Votre profil a été validé."),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,  # évite de casser l'admin si SMTP down
    )

    messages.success(request, _("Le profil a été validé et un e-mail a été envoyé."))
    return redirect("dashboard:pending_profiles")


# ======================================================
# REFUS PROFIL
# ======================================================
@staff_member_required
def refuse_profile_view(request, profile_id):
    profile = get_object_or_404(UserEconomicProfile, id=profile_id)
    user = profile.user

    profile.status = UserEconomicProfile.Status.REFUSED
    profile.save(update_fields=["status", "updated_at"])

    subject = _("Votre profil SOGENTIS a été refusé")
    html_message = render_to_string("accounts_users/emails/profile_refused.html", {"user": user, "profile": profile})

    send_mail(
        subject=subject,
        message=_("Votre profil n’a pas été validé."),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )

    messages.error(request, _("Le profil a été refusé et un e-mail a été envoyé."))
    return redirect("dashboard:pending_profiles")








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
