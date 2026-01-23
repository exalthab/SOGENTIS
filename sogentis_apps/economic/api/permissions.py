# economic/api/permissions.py
from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission

__all__ = ["IsVendor", "IsVerifiedVendor", "IsB2BAdmin"]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _is_authenticated_active_user(user) -> bool:
    """
    DRF appelle les permissions même si user est AnonymousUser.
    On sécurise aussi le cas user inactif.
    """
    return bool(
        user
        and getattr(user, "is_authenticated", False)
        and getattr(user, "is_active", True)
    )


def _get_related(user, attr: str):
    """
    Récupère un attribut lié (ex: user.vendor / user.company_user) sans planter.

    Gère :
    - AnonymousUser
    - attribut inexistant
    - OneToOne reverse absent (RelatedObjectDoesNotExist -> ObjectDoesNotExist)
    """
    try:
        return getattr(user, attr)
    except (AttributeError, ObjectDoesNotExist):
        return None


def _is_staff_or_superuser(user) -> bool:
    """Bypass pour les comptes à privilèges élevés."""
    return bool(
        user
        and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
    )


# ---------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------

class IsVendor(BasePermission):
    """Autorise uniquement les utilisateurs ayant un profil Vendor lié."""
    message = "Accès réservé aux vendeurs."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)

        if not _is_authenticated_active_user(user):
            return False

        if _is_staff_or_superuser(user):
            return True

        return _get_related(user, "vendor") is not None

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class IsVerifiedVendor(BasePermission):
    """Autorise uniquement les vendeurs vérifiés."""
    message = "Votre compte vendeur n'est pas encore vérifié."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)

        if not _is_authenticated_active_user(user):
            return False

        if _is_staff_or_superuser(user):
            return True

        vendor = _get_related(user, "vendor")
        return bool(vendor and getattr(vendor, "is_verified", False))

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class IsB2BAdmin(BasePermission):
    """
    Autorise uniquement les utilisateurs B2B admin
    (relation user.company_user avec is_admin=True).
    """
    message = "Accès réservé aux administrateurs B2B."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)

        if not _is_authenticated_active_user(user):
            return False

        if _is_staff_or_superuser(user):
            return True

        company_user = _get_related(user, "company_user")
        return bool(company_user and getattr(company_user, "is_admin", False))

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)







# # economic/api/permissions.py
# from __future__ import annotations

# from django.core.exceptions import ObjectDoesNotExist
# from rest_framework.permissions import BasePermission


# def _get_related(user, attr: str):
#     """
#     Récupère un attribut lié (ex: user.vendor / user.company_user) sans planter.
#     Gère :
#     - AnonymousUser (pas is_authenticated)
#     - OneToOne reverse absent (RelatedObjectDoesNotExist)
#     """
#     try:
#         return getattr(user, attr)
#     except (AttributeError, ObjectDoesNotExist):
#         return None


# class IsVendor(BasePermission):
#     """
#     Autorise uniquement les utilisateurs ayant un profil Vendor lié.
#     """

#     def has_permission(self, request, view):
#         user = getattr(request, "user", None)
#         if not user or not user.is_authenticated:
#             return False

#         # Bypass optionnel : staff/superuser
#         if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
#             return True

#         return _get_related(user, "vendor") is not None

#     def has_object_permission(self, request, view, obj):
#         return self.has_permission(request, view)


# class IsVerifiedVendor(BasePermission):
#     """
#     Autorise uniquement les Vendors vérifiés.
#     """

#     def has_permission(self, request, view):
#         user = getattr(request, "user", None)
#         if not user or not user.is_authenticated:
#             return False

#         if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
#             return True

#         vendor = _get_related(user, "vendor")
#         return bool(vendor and getattr(vendor, "is_verified", False))

#     def has_object_permission(self, request, view, obj):
#         return self.has_permission(request, view)


# class IsB2BAdmin(BasePermission):
#     """
#     Autorise uniquement les users B2B ayant company_user.is_admin=True.
#     """

#     def has_permission(self, request, view):
#         user = getattr(request, "user", None)
#         if not user or not user.is_authenticated:
#             return False

#         if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
#             return True

#         cu = _get_related(user, "company_user")
#         return bool(cu and getattr(cu, "is_admin", False))

#     def has_object_permission(self, request, view, obj):
#         return self.has_permission(request, view)






# # /economic/api/permissions.py

# from rest_framework.permissions import BasePermission


# class IsVendor(BasePermission):
#     def has_permission(self, request, view):
#         return hasattr(request.user, "vendor")


# class IsVerifiedVendor(BasePermission):
#     def has_permission(self, request, view):
#         return (
#             hasattr(request.user, "vendor")
#             and request.user.vendor.is_verified
#         )


# class IsB2BAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return (
#             hasattr(request.user, "company_user")
#             and request.user.company_user.is_admin
#         )
