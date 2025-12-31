# /economic/policies.py
# =====================================================
# Politiques d'accès simples et réutilisables
# =====================================================

from dashboard.permissions import is_admin as is_staff_admin
from economic.permissions import (
    is_vendor as is_vendor_user,
    is_verified_vendor,
    is_b2b_user as is_b2b,
    is_b2b_manager,
)


# -----------------------------------------------------
# VENDOR
# -----------------------------------------------------

def vendor_required(user):
    """Utilisateur lié à un profil vendeur (Marketplace)"""
    return is_vendor_user(user)


def verified_vendor_required(user):
    """Vendeur validé par l’administrateur"""
    return is_verified_vendor(user)


# -----------------------------------------------------
# B2B
# -----------------------------------------------------

def b2b_required(user):
    """Utilisateur B2B"""
    return is_b2b(user)


def b2b_admin_required(user):
    """Admin d’une entreprise B2B"""
    return is_b2b_manager(user)


# -----------------------------------------------------
# STAFF / ADMIN
# -----------------------------------------------------

def admin_required(user):
    """Staff ou superuser de la plateforme"""
    return is_staff_admin(user)






# # /economic/policies.py

# def is_vendor(user):
#     return hasattr(user, "vendor")

# def is_b2b_user(user):
#     return hasattr(user, "company_user")

# def is_admin(user):
#     return user.is_authenticated and user.is_staff
