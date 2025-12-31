# /dashboard/views/router.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .hub import dashboard_hub_view


@login_required
def dashboard_router(request):
    """
    Router central du dashboard.
    Utilise la même logique que dashboard_hub_view.
    Branché sur la racine de /dashboard/ (voir dashboard/urls.py).
    """
    return dashboard_hub_view(request)






# # dashboard/views/router.py

# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import (
#     is_admin,
#     is_vendor,
#     is_b2b_user,
# )


# @login_required
# def dashboard_router(request):
#     """
#     Router central du dashboard.
#     Redirige l'utilisateur selon son rôle principal.
#     Ordre de priorité :
#     1. Admin / Staff
#     2. Vendeur
#     3. B2B
#     4. Utilisateur standard
#     """

#     user = request.user

#     # =====================================================
#     # ADMIN / STAFF
#     # =====================================================
#     if is_admin(user) or user.is_staff:
#         return redirect("dashboard:admin_home")

#     # =====================================================
#     # VENDEUR
#     # =====================================================
#     if is_vendor(user):
#         return redirect("dashboard:vendor_index")

#     # =====================================================
#     # B2B
#     # =====================================================
#     if is_b2b_user(user):
#         return redirect("dashboard:b2b_home")

#     # =====================================================
#     # UTILISATEUR STANDARD
#     # =====================================================
#     return redirect("dashboard:user_home")




# # dashboard/views/router.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import (
#     is_admin,
#     is_vendor,
#     is_b2b_user,
# )


# @login_required
# def dashboard_router(request):
#     user = request.user

#     # if is_admin(user):
#     #     return redirect("dashboard:admin_home")

#     if is_vendor(user):
#         return redirect("dashboard:vendor_home")

#     if is_b2b_user(user):
#         return redirect("dashboard:b2b_home")

#     return redirect("dashboard:user_home")
