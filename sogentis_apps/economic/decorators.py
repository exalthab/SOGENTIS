# /economic/decorators.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from economic.permissions import (
    is_vendor,
    is_verified_vendor,
    is_b2b_user,
    is_b2b_manager,
    is_authenticated_user,
)
from dashboard.permissions import is_admin


# =====================================================
# UTILITAIRE : décorateur générique défensif
# =====================================================

def role_required(user_check, login_url="accounts_users_web:login"):
    """
    Décorateur générique :
    - Redirige vers login si non connecté
    - Lève PermissionDenied si connecté mais non autorisé
    """
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url)
            if not user_check(request.user):
                raise PermissionDenied("Accès refusé pour ce rôle")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# =====================================================
# PUBLIC / UTILISATEUR CONNECTÉ
# =====================================================

user_required = user_passes_test(
    lambda u: u.is_authenticated,
    login_url="accounts_users:login"
)


# =====================================================
# VENDOR
# =====================================================

vendor_required = role_required(is_vendor)
verified_vendor_required = role_required(is_verified_vendor)


# =====================================================
# B2B
# =====================================================

b2b_required = role_required(is_b2b_user)
b2b_admin_required = role_required(is_b2b_manager)


# =====================================================
# STAFF / ADMIN
# =====================================================

staff_required = role_required(is_admin)


# =====================================================
# UTILITAIRES SUPPLÉMENTAIRES
# =====================================================

def any_role_required(*checks):
    """
    Décorateur flexible pour autoriser plusieurs rôles
    Exemple :
        @any_role_required(is_b2b_user, is_vendor, is_admin)
    """
    def _combined(user):
        return any(check(user) for check in checks)
    return role_required(_combined)


# =====================================================
# HIÉRARCHIE COMPLÈTE (OPTIONNEL)
# =====================================================

# Ces décorateurs sont pratiques pour les vues où la hiérarchie complète doit être respectée
vendor_or_b2b_required = any_role_required(is_vendor, is_b2b_user)
b2b_or_staff_required = any_role_required(is_b2b_user, is_b2b_manager, is_admin)



# # /economic/decorators.py

# from django.contrib.auth.decorators import user_passes_test
# from economic.permissions import (
#     is_vendor,
#     is_verified_vendor,
#     is_b2b_admin,
# )


# vendor_required = user_passes_test(
#     is_vendor,
#     login_url="accounts_users:login",
# )


# verified_vendor_required = user_passes_test(
#     is_verified_vendor,
#     login_url="accounts_users:login",
# )


# b2b_admin_required = user_passes_test(
#     is_b2b_admin,
#     login_url="accounts_users:login",
# )
