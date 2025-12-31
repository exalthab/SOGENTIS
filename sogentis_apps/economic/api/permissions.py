# sogentis_apps/economic/api/permissions.py

from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "vendor")


class IsVerifiedVendor(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "vendor")
            and request.user.vendor.is_verified
        )


class IsB2BAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "company_user")
            and request.user.company_user.is_admin
        )
