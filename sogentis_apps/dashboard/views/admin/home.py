# dashboard/views/admin/home.py

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user


@login_required
def admin_home_view(request):
    """
    Dashboard Administrateur / Staff.
    Utilise tes helpers is_admin et is_staff_user.
    """
    user = request.user

    if is_admin(user):
        page_title = _("Administration")
    elif is_staff_user(user):
        page_title = _("Espace staff")
    else:
        # Pas admin, pas staff → accès refusé
        raise PermissionDenied

    return render(
        request,
        "dashboard/admin/home.html",
        {
            "page_title": page_title,
            # "dashboard_menu": "dashboard/admin/_menu.html",  # si tu veux plus tard
        },
    )

















# # dashboard/views/admin/home.py

# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user


# @login_required
# @user_passes_test(is_admin)
# def admin_dashboard_home_view(request):
#     """
#     Dashboard Administrateur
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Administration"),
#             # "section_menu": "dashboard/admin/_menu.html",
#             "dashboard_menu": "dashboard/admin/_menu.html",

#         }
#     )


# @login_required
# @user_passes_test(is_staff_user)
# def staff_dashboard_home_view(request):
#     """
#     Dashboard Staff (support, modération, etc.)
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Espace staff"),
#             # "section_menu": "dashboard/admin/_menu.html",
#             "dashboard_menu": "dashboard/admin/_menu.html",

#         }
#     )






# # dashboard/views/admin/home.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user


# @login_required
# @user_passes_test(is_admin)
# def admin_dashboard_home_view(request):
#     """
#     Dashboard Administrateur
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Administration"),
#         }
#     )


# @login_required
# @user_passes_test(is_staff_user)
# def staff_dashboard_home_view(request):
#     """
#     Dashboard Staff (support, modération, etc.)
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Espace Staff"),
#         }
#     )







# # dashboard/views/admin/home.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user


# @login_required
# @user_passes_test(is_admin)
# def admin_home(request):
#     """
#     Accès administrateur plateforme
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Administration"),
#         }
#     )


# @login_required
# @user_passes_test(is_staff_user)
# def staff_dashboard_home(request):
#     """
#     Accès staff (support, modération, etc.)
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Espace Staff"),
#         }
#     )







# # dashboard/views/admin/home.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_admin, is_staff_user
# from django.utils.translation import gettext_lazy as _


# def is_staff_user(user):
#     return user.is_authenticated and user.is_staff


# @login_required
# @user_passes_test(is_admin)
# def admin_home(request):
#     return render(request,"dashboard/admin/home.html")


# @login_required
# @user_passes_test(is_staff_user)
# def admin_dashboard_home_view(request):
#     """
#     Dashboard Admin / Staff
#     """
#     return render(
#         request,
#         "dashboard/admin/home.html",
#         {
#             "page_title": _("Administration"),
#         }
#     )