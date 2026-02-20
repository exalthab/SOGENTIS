# economic/permissions.py
from __future__ import annotations


# -----------------------------------------------------
# UTILITAIRES
# -----------------------------------------------------
def is_authenticated_user(user) -> bool:
    return bool(user and getattr(user, "is_authenticated", False))


def is_staff(user) -> bool:
    return is_authenticated_user(user) and bool(getattr(user, "is_staff", False))


def _get_company_user(user):
    """
    Retourne un CompanyUser valide (actif + entreprise active) sinon None.
    Défensif : ne crash pas si relations absentes.
    """
    if not is_authenticated_user(user):
        return None

    cu = getattr(user, "company_user", None)  # ton mapping actuel
    if not cu:
        return None

    if not getattr(cu, "is_active", True):
        return None

    company = getattr(cu, "company", None)
    if not company or not getattr(company, "is_active", True):
        return None

    return cu


# -----------------------------------------------------
# VENDOR (Marketplace)
# -----------------------------------------------------
def is_vendor(user) -> bool:
    if not is_authenticated_user(user):
        return False
    v = getattr(user, "vendor", None)
    return bool(v)


def is_verified_vendor(user) -> bool:
    if not is_vendor(user):
        return False
    v = getattr(user, "vendor", None)
    return bool(v and getattr(v, "is_verified", False))


# -----------------------------------------------------
# B2B (Entreprise)
# -----------------------------------------------------
def is_b2b_user(user) -> bool:
    return _get_company_user(user) is not None


def is_b2b_admin(user) -> bool:
    cu = _get_company_user(user)
    return bool(cu and getattr(cu, "is_admin", False))


def is_b2b_manager(user) -> bool:
    cu = _get_company_user(user)
    if not cu:
        return False
    if getattr(cu, "is_admin", False):
        return True
    return (getattr(cu, "role", "") or "").lower() in {"staff", "manager"}


# -----------------------------------------------------
# NIVEAU PRINCIPAL
# -----------------------------------------------------
def get_user_level(user) -> str:
    """
    public → user → vendor → verified_vendor → b2b → b2b_admin → staff
    """
    if not is_authenticated_user(user):
        return "public"

    if is_staff(user):
        return "staff"

    if is_b2b_admin(user):
        return "b2b_admin"

    if is_b2b_user(user):
        return "b2b"

    if is_verified_vendor(user):
        return "verified_vendor"

    if is_vendor(user):
        return "vendor"

    return "user"







# # economic/permissions.py
# # =====================================================
# # Policy de base : rôles économiques
# # =====================================================

# # -----------------------------------------------------
# # UTILITAIRES
# # -----------------------------------------------------

# def is_authenticated_user(user):
#     """Utilisateur connecté"""
#     return bool(user and user.is_authenticated)


# def is_staff(user):
#     """Utilisateur staff / admin Django"""
#     return is_authenticated_user(user) and user.is_staff


# def _get_company_user(user):
#     """
#     Retourne un CompanyUser valide (actif + entreprise active),
#     sinon None. Défensif en production.
#     """
#     if not is_authenticated_user(user):
#         return None

#     cu = getattr(user, "company_user", None)
#     if not cu:
#         return None

#     # CompanyUser actif ?
#     if not getattr(cu, "is_active", True):
#         return None

#     # Entreprise active ?
#     company = getattr(cu, "company", None)
#     if not company or not getattr(company, "is_active", True):
#         return None

#     return cu


# # -----------------------------------------------------
# # VENDOR (Marketplace)
# # -----------------------------------------------------

# def is_vendor(user):
#     """
#     Utilisateur lié à un profil vendeur (Marketplace)
#     Défensif : ne crash pas si relation absente
#     """
#     return is_authenticated_user(user) and hasattr(user, "vendor")


# def is_verified_vendor(user):
#     """
#     Vendeur vérifié par l'administrateur
#     """
#     return is_vendor(user) and getattr(user.vendor, "is_verified", False)


# # -----------------------------------------------------
# # B2B (Entreprise)
# # -----------------------------------------------------

# def is_b2b_user(user):
#     """
#     Utilisateur rattaché à une entreprise B2B (CompanyUser actif + company active)
#     """
#     return _get_company_user(user) is not None


# def is_b2b_admin(user):
#     """
#     Admin d'une entreprise B2B (selon ton modèle CompanyUser.is_admin)
#     """
#     cu = _get_company_user(user)
#     return bool(cu and getattr(cu, "is_admin", False))


# def is_b2b_manager(user):
#     """
#     Manager B2B : admin OU staff (role CompanyUser)
#     - admin : cu.is_admin True
#     - staff : role == "staff"
#     """
#     cu = _get_company_user(user)
#     if not cu:
#         return False
#     if getattr(cu, "is_admin", False):
#         return True
#     return getattr(cu, "role", "") == "staff"


# # -----------------------------------------------------
# # NIVEAU PRINCIPAL
# # -----------------------------------------------------

# def get_user_level(user):
#     """
#     Retourne le niveau principal de l'utilisateur selon la hiérarchie :

#     public → user → vendor → verified_vendor → b2b → b2b_admin → staff
#     """
#     if not is_authenticated_user(user):
#         return "public"

#     if is_staff(user):
#         return "staff"

#     # b2b_admin = admin only (strict)
#     if is_b2b_admin(user):
#         return "b2b_admin"

#     # b2b = tout utilisateur B2B valide
#     if is_b2b_user(user):
#         return "b2b"

#     if is_verified_vendor(user):
#         return "verified_vendor"

#     if is_vendor(user):
#         return "vendor"

#     return "user"






# # /economic/permissions.py
# # =====================================================
# # Policy de base : rôles économiques
# # =====================================================

# from django.conf import settings

# # -----------------------------------------------------
# # UTILITAIRES
# # -----------------------------------------------------

# def is_authenticated_user(user):
#     """Utilisateur connecté"""
#     return bool(user and user.is_authenticated)


# def is_staff(user):
#     """Utilisateur staff / admin Django"""
#     return is_authenticated_user(user) and user.is_staff


# # -----------------------------------------------------
# # VENDOR (Marketplace)
# # -----------------------------------------------------

# def is_vendor(user):
#     """
#     Utilisateur lié à un profil vendeur (Marketplace)
#     Défensif : ne crash pas si relation absente
#     """
#     return is_authenticated_user(user) and hasattr(user, "vendor")


# def is_verified_vendor(user):
#     """
#     Vendeur vérifié par l'administrateur
#     """
#     return is_vendor(user) and getattr(user.vendor, "is_verified", False)


# # -----------------------------------------------------
# # B2B (Entreprise)
# # -----------------------------------------------------

# def is_b2b_user(user):
#     """
#     Utilisateur rattaché à une entreprise B2B
#     """
#     return is_authenticated_user(user) and hasattr(user, "company_user")


# def is_b2b_admin(user):
#     """
#     Admin d'une entreprise B2B
#     """
#     return is_b2b_user(user) and getattr(user.company_user, "is_admin", False)


# def is_b2b_manager(user):
#     """
#     Alias explicite pour un manager B2B (admin ou responsable)
#     """
#     return is_b2b_admin(user)


# # -----------------------------------------------------
# # NIVEAU PRINCIPAL
# # -----------------------------------------------------

# def get_user_level(user):
#     """
#     Retourne le niveau principal de l'utilisateur selon la hiérarchie :

#     public → user → vendor → verified_vendor → b2b → b2b_admin → staff
#     """
#     if not is_authenticated_user(user):
#         return "public"

#     if is_staff(user):
#         return "staff"

#     if is_b2b_admin(user):
#         return "b2b_admin"

#     if is_b2b_user(user):
#         return "b2b"

#     if is_verified_vendor(user):
#         return "verified_vendor"

#     if is_vendor(user):
#         return "vendor"

#     return "user"



# # sogentis_apps/economic/permissions.py
# """
# Permissions globales du pôle économique
# (extensions futures possibles)
# """

# def is_economic_staff(user):
#     return bool(user and user.is_authenticated and user.is_staff)
