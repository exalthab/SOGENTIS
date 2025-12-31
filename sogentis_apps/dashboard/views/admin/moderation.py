# dashboard/views/admin/moderation.py
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user

try:
    # ⚠️ mets ici le BON modèle de profil qui est utilisé pour validation
    # ex: accounts_users.models.users_profile.UserProfile (social)
    from accounts_users.models.users_profile import UserProfile
except Exception:
    UserProfile = None


def _is_staff_or_admin(user):
    return is_admin(user) or is_staff_user(user)


@login_required
def admin_moderation_view(request):
    """
    Modération globale:
    - profils en attente (si supporté par le modèle)
    """
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    pending_profiles = []

    if UserProfile is not None:
        # ✅ filtre seulement si le champ existe réellement
        profile_fields = {f.name for f in UserProfile._meta.get_fields()}

        if "status" in profile_fields:
            qs = UserProfile.objects.filter(status="pending")
        elif "is_validated" in profile_fields:
            qs = UserProfile.objects.filter(is_validated=False)
        elif "is_approved" in profile_fields:
            qs = UserProfile.objects.filter(is_approved=False)
        else:
            qs = UserProfile.objects.none()

        # ✅ select_related seulement si relation existe
        select_related_fields = ["user"]
        if "membership_role" in profile_fields:
            select_related_fields.append("membership_role")

        pending_profiles = qs.select_related(*select_related_fields).order_by("created_at")

    context = {
        "page_title": _("Modération"),
        "pending_profiles": pending_profiles,
    }
    return render(request, "dashboard/admin/moderation.html", context)






# # dashboard/views/admin/moderation.py
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# try:
#     from accounts_users.models.users_profile import UserProfile
# except Exception:
#     UserProfile = None


# def _is_staff_or_admin(user):
#     return is_admin(user) or is_staff_user(user)


# @login_required
# def admin_moderation_view(request):
#     """
#     Écran de modération globale :
#     - profils en attente
#     - prêt à accueillir signalements / logs plus tard
#     """
#     user = request.user
#     if not _is_staff_or_admin(user):
#         raise PermissionDenied

#     pending_profiles = []
#     if UserProfile is not None:
#         pending_profiles = (
#             UserProfile.objects.filter(status="pending")
#             .select_related("user", "membership_role")
#             .order_by("created_at")
#         )

#     context = {
#         "page_title": _("Modération"),
#         "pending_profiles": pending_profiles,
#     }
#     return render(request, "dashboard/admin/moderation.html", context)





# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_admin


# @login_required
# @user_passes_test(is_admin)
# def moderation_dashboard(request):
#     return render(request, "dashboard/admin/moderation.html")
