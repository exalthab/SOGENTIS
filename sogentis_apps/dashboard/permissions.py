from django.apps import apps


# =====================================================
# UTILITAIRES
# =====================================================

def _safe_user(user) -> bool:
    """Utilisateur valide et authentifié"""
    return bool(user and user.is_authenticated)


# =====================================================
# STAFF / ADMIN
# =====================================================

def is_staff_user(user) -> bool:
    """Staff Django (back-office, modération, etc.)"""
    return _safe_user(user) and user.is_staff


def is_admin(user) -> bool:
    """Administrateur plateforme (niveau le plus élevé)"""
    return (
        _safe_user(user)
        and (
            user.is_superuser
            or user.groups.filter(name="ADMIN").exists()
        )
    )


# =====================================================
# MANAGERS MÉTIER
# =====================================================

def is_social_manager(user) -> bool:
    return _safe_user(user) and user.groups.filter(name="SOCIAL_MANAGER").exists()


def is_economic_manager(user) -> bool:
    return _safe_user(user) and user.groups.filter(name="ECONOMIC_MANAGER").exists()


# =====================================================
# ROLES ÉCONOMIQUES
# =====================================================

def is_vendor(user) -> bool:
    """Vendeur marketplace"""
    if not _safe_user(user):
        return False
    if not apps.is_installed("economic.ecommerce"):
        return False
    return hasattr(user, "vendor")


def is_verified_vendor(user) -> bool:
    return is_vendor(user) and getattr(user.vendor, "is_verified", False)


def is_b2b_user(user) -> bool:
    if not _safe_user(user):
        return False
    if not apps.is_installed("economic.b2b"):
        return False
    return hasattr(user, "company_user")


def is_b2b_manager(user) -> bool:
    return is_b2b_user(user) and getattr(user.company_user, "role", "") == "ADMIN"


# =====================================================
# NIVEAU UTILISATEUR (CENTRAL)
# =====================================================

def get_user_level(user) -> str:
    """
    Niveau principal (ordre strict de priorité)
    """
    if not _safe_user(user):
        return "public"

    if is_admin(user):
        return "admin"

    if is_staff_user(user):
        return "staff"

    if is_b2b_manager(user):
        return "b2b_manager"

    if is_b2b_user(user):
        return "b2b"

    if is_verified_vendor(user):
        return "verified_vendor"

    if is_vendor(user):
        return "vendor"

    return "user"







# # dashboard/permissions.py
# from django.apps import apps


# # =====================================================
# # UTILITAIRES
# # =====================================================

# def _safe_user(user):
#     """Vérifie que l'utilisateur existe et est authentifié"""
#     return bool(user and user.is_authenticated)


# # =====================================================
# # ROLES STAFF / ADMIN
# # =====================================================

# def is_admin(user):
#     """Administrateur plateforme"""
#     return (
#         _safe_user(user)
#         and (
#             user.is_superuser
#             or user.is_staff
#             or user.groups.filter(name="ADMIN").exists()
#         )
#     )


# # =====================================================
# # MANAGERS / ROLES METIER
# # =====================================================

# def is_social_manager(user):
#     return _safe_user(user) and user.groups.filter(name="SOCIAL_MANAGER").exists()


# def is_economic_manager(user):
#     return _safe_user(user) and user.groups.filter(name="ECONOMIC_MANAGER").exists()


# # =====================================================
# # ROLES ECONOMIQUES
# # =====================================================

# def is_vendor(user):
#     """Utilisateur vendeur (Marketplace)"""
#     if not _safe_user(user):
#         return False
#     if not apps.is_installed("economic.ecommerce"):
#         return False
#     return hasattr(user, "vendor")


# def is_verified_vendor(user):
#     """Vendeur vérifié par l'admin"""
#     return is_vendor(user) and getattr(user.vendor, "is_verified", False)


# def is_b2b(user):
#     """Utilisateur B2B (entreprise)"""
#     if not _safe_user(user):
#         return False
#     if not apps.is_installed("economic.b2b"):
#         return False
#     return hasattr(user, "company_user")


# def is_b2b_user(user):
#     """Alias explicite pour lisibilité"""
#     return is_b2b(user)


# def is_b2b_manager(user):
#     """Admin d'une entreprise B2B"""
#     return is_b2b(user) and getattr(user.company_user, "role", "") == "ADMIN"


# # =====================================================
# # NIVEAU UTILISATEUR (POINT CENTRAL)
# # =====================================================

# def get_user_level(user):
#     """
#     Retourne le niveau principal de l'utilisateur.
#     Hiérarchie complète :
#     public → user → vendor → verified_vendor → b2b → b2b_manager → staff
#     """
#     if not _safe_user(user):
#         return "public"

#     if is_admin(user):
#         return "staff"

#     if is_b2b_manager(user):
#         return "b2b_manager"

#     if is_b2b(user):
#         return "b2b"

#     if is_verified_vendor(user):
#         return "verified_vendor"

#     if is_vendor(user):
#         return "vendor"

#     return "user"





# # dashboard/permissions.py

# from django.apps import apps


# def _safe_user(user):
#     return bool(user and user.is_authenticated)


# # =========================
# # MANAGERS / ROLES METIER
# # =========================

# def is_social_manager(user):
#     return (
#         _safe_user(user)
#         and user.groups.filter(name="SOCIAL_MANAGER").exists()
#     )


# def is_economic_manager(user):
#     return (
#         _safe_user(user)
#         and user.groups.filter(name="ECONOMIC_MANAGER").exists()
#     )


# def is_admin(user):
#     return (
#         _safe_user(user)
#         and (
#             user.is_superuser
#             or user.groups.filter(name="ADMIN").exists()
#         )
#     )


# # =========================
# # ROLES ECONOMIQUES
# # =========================

# def is_vendor(user):
#     """
#     Utilisateur vendeur (Marketplace)
#     Défensif : ne casse pas si l'app n'est pas prête.
#     """
#     if not _safe_user(user):
#         return False

#     if not apps.is_installed("economic.ecommerce"):
#         return False

#     try:
#         return hasattr(user, "vendor")
#     except Exception:
#         return False


# def is_b2b(user):
#     """
#     Utilisateur B2B (entreprise)
#     Défensif : ne touche pas la DB si la table n'existe pas.
#     """
#     if not _safe_user(user):
#         return False

#     if not apps.is_installed("economic.b2b"):
#         return False

#     try:
#         return hasattr(user, "company_user")
#     except Exception:
#         return False


# def is_b2b_user(user):
#     """
#     Alias explicite pour lisibilité dans les vues
#     """
#     return is_b2b(user)

# def is_b2b_manager(user):
#     return (
#         user.is_authenticated
#         and hasattr(user, "company_user")
#         and user.company_user.role == "ADMIN"
#     )
