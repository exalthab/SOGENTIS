# accounts_users/admin/admin_role.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from accounts_users.admin.admin_base import BaseAdmin
from accounts_users.models.admin_roles import AdminRole
from accounts_users.models.user_role import UserRole
from accounts_users.models.membership_role import MembershipRole


@admin.register(AdminRole)
class AdminRoleAdmin(BaseAdmin):
    list_display = ("label", "is_active", "created_at_display", "updated_at_display")
    search_fields = ("label",)
    list_filter = ("is_active",)


@admin.register(UserRole)
class UserRoleAdmin(BaseAdmin):
    list_display = ("code", "is_active", "created_at_display")
    list_filter = ("is_active",)
    search_fields = ("code",)


@admin.register(MembershipRole)
class MembershipRoleAdmin(BaseAdmin):
    list_display = ("code", "label", "created_at_display")
    search_fields = ("code", "label")






# # accounts_users/admin/admin_role.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.admin.admin_base import BaseAdmin
# from accounts_users.models.admin_roles import AdminRole
# from accounts_users.models.user_role import UserRole
# from accounts_users.models.membership_role import MembershipRole


# # ======================================================
# # RÔLES ADMINISTRATEURS (Admin, Moderator, etc.)
# # ======================================================

# @admin.register(AdminRole)
# class AdminRoleAdmin(BaseAdmin):
#     """
#     Administration des rôles administrateurs
#     (admin, moderator, superuser, etc.)
#     """

#     list_display = (
#         "description",
#         "is_active",
#         "created_at_display",
#         "updated_at_display",
#     )

#     list_filter = (
#         "is_active",
#     )

#     search_fields = (
#         "description",
#     )

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#     )

#     fieldsets = (
#         (
#             _("Informations du rôle"),
#             {
#                 "fields": (
#                     "description",
#                     "is_active",
#                 )
#             },
#         ),
#         (
#             _("Métadonnées"),
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 )
#             },
#         ),
#     )


# # ======================================================
# # RÔLES ADMINISTRATIFS UTILISATEUR (Staff / Admin / Moderator)
# # ======================================================

# @admin.register(UserRole)
# class UserRoleAdmin(BaseAdmin):
#     """
#     Rôles liés aux permissions administratives utilisateur
#     """

#     list_display = (
#         "code",
#         "label",
#         "is_active_display",
#         "created_at_display",
#         "updated_at_display",
#     )

#     list_filter = (
#         "is_active",
#     )

#     search_fields = (
#         "code",
#         "label",
#     )

#     @admin.display(description=_("Actif"), ordering="is_active")
#     def is_active_display(self, obj):
#         return "✅" if obj.is_active else "❌"


# # ======================================================
# # RÔLES D’ADHÉSION / SOCIAUX
# # ======================================================

# @admin.register(MembershipRole)
# class MembershipRoleAdmin(BaseAdmin):
#     """
#     Rôles d’adhésion (social, membre, invité, etc.)
#     """

#     list_display = (
#         "code",
#         "label",
#         "created_at_display",
#         "updated_at_display",
#     )

#     search_fields = (
#         "code",
#         "label",
#         "description",
#     )