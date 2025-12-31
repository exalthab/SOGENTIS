# /dashboard/views/hub.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from dashboard.permissions import (
    is_staff_user,
    is_admin,
    is_vendor,
    is_b2b_user,
)
from accounts_users.services.users_service import has_social_role


@login_required
def dashboard_hub_view(request):
    """
    Point d’entrée UNIQUE après login.
    Redirection par priorité métier.
    Ordre de priorité :
      1. Admin / Staff
      2. Vendeur B2C
      3. B2B
      4. Social
      5. Utilisateur standard
    """
    user = request.user

    # 1) ADMIN / STAFF
    if is_admin(user) or user.is_staff or is_staff_user(user):
        # Namespace "admin" défini dans dashboard/urls.py :
        # path("admin/", include(("dashboard.urls.admin", "admin"), namespace="admin"))
        return redirect("dashboard:admin:home")

    # 2) VENDEUR B2C
    if is_vendor(user):
        # Nom défini dans dashboard/urls.py : name="vendor_home"
        return redirect("dashboard:vendor_home")

    # 3) B2B
    if is_b2b_user(user):
        # Nom défini dans dashboard/urls.py : name="b2b_home"
        return redirect("dashboard:b2b_home")

    # 4) SOCIAL (donateur, membre, volontaire, etc.)
    if has_social_role(user):
        # Router social défini dans dashboard/urls.py : name="social_router"
        return redirect("dashboard:social_router")

    # 5) UTILISATEUR STANDARD (dashboard utilisateur)
    # Nom défini dans dashboard/urls.py :
    #   path("user/", user_dashboard_home_view, name="home")
    return redirect("dashboard:home")






# # /dashboard/views/hub.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import is_staff_user, is_admin, is_vendor, is_b2b_user
# from accounts_users.services.users_service import has_social_role


# @login_required
# def dashboard_hub_view(request):
#     """
#     Point d’entrée UNIQUE après login.
#     Redirection par priorité métier.
#     """
#     user = request.user

#     # ADMIN / STAFF
#     if is_admin(user) or user.is_staff:
#         return redirect("dashboard:admin:home")
    
#     if is_admin(user):
#         return redirect("dashboard:admin:home")

#     if is_staff_user(user):
#         return redirect("dashboard:admin:staff")


#     # VENDEUR B2C
#     if is_vendor(user):
#         return redirect("dashboard:vendor:vendor_index")

#     # B2B
#     if is_b2b_user(user):
#         return redirect("dashboard:b2b:home")

#     # SOCIAL
#     if has_social_role(user):
#         return redirect("dashboard:social:home")

#     # UTILISATEUR STANDARD
#     return redirect("dashboard:user:home")





# # dashboard/views/hub.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import is_admin, is_vendor, is_b2b_user
# from accounts_users.services import has_social_role  # à adapter si besoin

# @login_required
# def dashboard_hub_view(request):
#     """
#     Point d’entrée UNIQUE après login.
#     Redirige selon le rôle principal.
#     """
#     user = request.user

#     # ADMIN / STAFF
#     if is_admin(user) or user.is_staff:
#         return redirect("dashboard:admin_home")

#     # VENDEUR (B2C)
#     if is_vendor(user):
#         return redirect("dashboard:vendor:vendor_index")

#     # B2B
#     if is_b2b_user(user):
#         return redirect("dashboard:b2b:home")

#     # SOCIAL (donateur, membre, volontaire, institution)
#     if has_social_role(user):
#         return redirect("dashboard:social:home")

#     # CLIENT ÉCO STANDARD
#     return redirect("dashboard:user:home")











# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from dashboard.permissions import is_vendor, is_b2b_user


# @login_required
# def dashboard_hub_view(request):
#     """
#     Hub central : choix du pôle
#     """

#     context = {
#         "has_social_access": hasattr(request.user, "profile") and request.user.profile.membership_role,
#         "has_eco_access": is_vendor(request.user) or is_b2b_user(request.user),
#     }

#     return render(request, "dashboard/hub.html", context)
