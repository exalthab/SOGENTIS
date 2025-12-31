# dashboard/views/admin/users.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user

User = get_user_model()


def _is_staff_or_admin(user):
    return is_admin(user) or is_staff_user(user)


@login_required
def admin_users_list_view(request):
    """
    Liste des utilisateurs pour l’admin.
    - Recherche simple via ?q=
    """
    user = request.user
    if not _is_staff_or_admin(user):
        raise PermissionDenied

    q = (request.GET.get("q") or "").strip()

    users_qs = User.objects.all().order_by("-date_joined")

    if q:
        users_qs = users_qs.filter(
            Q(email__icontains=q) |
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    context = {
        "page_title": _("Utilisateurs"),
        "users": users_qs,
    }
    return render(request, "dashboard/admin/users_list.html", context)





# # dashboard/views/admin/users.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.contrib.auth import get_user_model
# from dashboard.permissions import is_admin

# User = get_user_model()


# @login_required
# @user_passes_test(is_admin)
# def users_list(request):
#     users = User.objects.all().order_by("-date_joined")
#     return render(
#         request,
#         "dashboard/admin/users.html",
#         {"users": users},
#     )
