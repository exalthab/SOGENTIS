from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext as _
from accounts_users.models.users_economic_profile import UserProfile
from accounts_users.services.profile_validation_service import send_profile_status_email


@staff_member_required
def validate_profile_view(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id)
    profile.status = "approved"
    profile.save()

    send_profile_status_email(profile.user, "approved")

    messages.success(request, _("Le profil a été validé. L’utilisateur a été notifié."))
    return redirect("dashboard:pending_profiles")


@staff_member_required
def refuse_profile_view(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id)
    profile.status = "refused"
    profile.save()

    send_profile_status_email(profile.user, "refused")

    messages.warning(request, _("Le profil a été refusé. L’utilisateur a été notifié."))
    return redirect("dashboard:pending_profiles")
