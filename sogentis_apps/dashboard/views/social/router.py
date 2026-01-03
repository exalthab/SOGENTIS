# dashboard/views/social/router.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import get_user_profile


@login_required
def social_dashboard_router(request):
    profile = get_user_profile(request.user)
    if profile and hasattr(profile, "role") and profile.role:
        code = getattr(profile.role, "code", "") or getattr(profile.role, "slug", "")
        code = (code or "").upper()

        if code in {"SPONSOR", "DONOR"}:
            return redirect("dashboard:social:donor_home")
        if code in {"VOLUNTEER"}:
            return redirect("dashboard:social:volunteer_home")
        if code in {"MEMBER"}:
            return redirect("dashboard:social:member_home")
        if code in {"INSTITUTION"}:
            return redirect("dashboard:social:institution_home")

    return redirect("dashboard:social:router_page")





# # dashboard/views/social/router.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from accounts_users.models import UserProfile


# @login_required
# def social_dashboard_router(request):
#     """
#     Router du pôle social
#     Redirige selon le rôle d'adhésion (membership)
#     """

#     profile = UserProfile.objects.select_related("membership_role").get(user=request.user)
#     role = profile.membership_role.code if profile.membership_role else None

#     if role == "DONOR":
#         return redirect("dashboard:social_donor_home")

#     if role == "MEMBER":
#         return redirect("dashboard:social_member_home")

#     if role == "VOLUNTEER":
#         return redirect("dashboard:social_volunteer_home")

#     if role == "INSTITUTION":
#         return redirect("dashboard:social_institution_home")

#     if role == "BENEFICIARY":
#         return redirect("dashboard:social_beneficiary_home")

#     return redirect("dashboard:social_default")
