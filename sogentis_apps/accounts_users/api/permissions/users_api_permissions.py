# apps/accounts_users/api/permissions/users_api_permissions.py
from rest_framework import permissions

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permet à un utilisateur de voir ou modifier uniquement son propre profil,
    sauf s'il est admin.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
