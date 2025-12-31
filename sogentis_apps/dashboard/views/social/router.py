# dashboard/views/social/router.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from accounts_users.models import UserProfile


@login_required
def social_dashboard_router(request):
    """
    Router du pôle social
    Redirige selon le rôle d'adhésion (membership)
    """

    profile = UserProfile.objects.select_related("membership_role").get(user=request.user)
    role = profile.membership_role.code if profile.membership_role else None

    if role == "DONOR":
        return redirect("dashboard:social_donor_home")

    if role == "MEMBER":
        return redirect("dashboard:social_member_home")

    if role == "VOLUNTEER":
        return redirect("dashboard:social_volunteer_home")

    if role == "INSTITUTION":
        return redirect("dashboard:social_institution_home")

    if role == "BENEFICIARY":
        return redirect("dashboard:social_beneficiary_home")

    return redirect("dashboard:social_default")
