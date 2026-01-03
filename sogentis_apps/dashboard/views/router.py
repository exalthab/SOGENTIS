# dashboard/views/router.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from dashboard.views.utils import get_user_profile


@login_required
def dashboard_router(request):
    """
    Router global dashboard (production).

    Règles:
    1) Staff/Admin -> dashboard admin
    2) Selon rôle membership (Social) -> pages social dédiées
    3) Sinon -> hub (home dashboard)
    """
    user = request.user

    # 1) STAFF / ADMIN
    if user.is_staff or user.is_superuser:
        # ✅ adapte selon tes urls admin:
        # - dans _sidebar_premium.html tu as: {% url 'dashboard:admin:index' %}
        # Donc on utilise "dashboard:admin:index".
        return redirect("dashboard:admin:index")

    # 2) ROLE (membership) — via profile.role.code / slug
    profile = get_user_profile(user)
    role_code = ""

    if profile is not None:
        role = getattr(profile, "role", None)
        if role:
            role_code = (getattr(role, "code", "") or getattr(role, "slug", "") or "").upper()

    # Social routes (si tu as ces noms exacts)
    if role_code in {"SPONSOR", "DONOR"}:
        # si tu as un nom plus simple, tu peux changer ici
        try:
            return redirect("dashboard:social:donor_home")
        except Exception:
            return redirect("dashboard:social:index")

    if role_code in {"VOLUNTEER"}:
        try:
            return redirect("dashboard:social:volunteer_home")
        except Exception:
            return redirect("dashboard:social:index")

    if role_code in {"MEMBER"}:
        try:
            return redirect("dashboard:social:member_home")
        except Exception:
            return redirect("dashboard:social:index")

    if role_code in {"INSTITUTION"}:
        try:
            return redirect("dashboard:social:institution_home")
        except Exception:
            return redirect("dashboard:social:index")

    # 3) DEFAULT
    return redirect("dashboard:hub")








# # dashboard/views/router.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect
# from django.urls import reverse

# from dashboard.views.utils import get_user_profile


# @login_required
# def dashboard_router(request):
#     """
#     Router global dashboard:
#     - staff -> hub
#     - sinon redirige vers hub (qui propose les espaces)
#     """
#     if request.user.is_staff:
#         return redirect("dashboard:hub")

#     # Si tu veux router automatiquement selon rôle membership:
#     profile = get_user_profile(request.user)
#     if profile and hasattr(profile, "role") and profile.role:
#         code = getattr(profile.role, "code", "") or getattr(profile.role, "slug", "")
#         code = (code or "").upper()
#         if code in {"SPONSOR", "DONOR"}:
#             return redirect("dashboard:social:donor_home")
#         if code in {"VOLUNTEER"}:
#             return redirect("dashboard:social:volunteer_home")
#         if code in {"MEMBER"}:
#             return redirect("dashboard:social:member_home")
#         if code in {"INSTITUTION"}:
#             return redirect("dashboard:social:institution_home")

#     return redirect("dashboard:hub")





# # /dashboard/views/router.py

# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from .hub import dashboard_hub_view


# @login_required
# def dashboard_router(request):
#     """
#     Router central du dashboard.
#     Utilise la même logique que dashboard_hub_view.
#     Branché sur la racine de /dashboard/ (voir dashboard/urls.py).
#     """
#     return dashboard_hub_view(request)






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
