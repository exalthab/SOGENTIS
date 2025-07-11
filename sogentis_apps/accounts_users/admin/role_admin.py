# accounts_users/admin/role_admin.py

from django.contrib import admin
from accounts_users.models.user_role import UserRole
from accounts_users.models.membership_role import MembershipRole

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "active_status", "created", "updated")
    list_filter = ("is_active",)
    search_fields = ("code", "label")
    ordering = ("-created_at",)
    readonly_fields = ("created", "updated")

    def active_status(self, obj):
        return "✅" if obj.is_active else "❌"
    active_status.short_description = "Actif"

    def created(self, obj):
        return obj.created_at
    created.admin_order_field = "created_at"
    created.short_description = "Créé le"

    def updated(self, obj):
        return obj.updated_at
    updated.admin_order_field = "updated_at"
    updated.short_description = "Mis à jour le"

@admin.register(MembershipRole)
class MembershipRoleAdmin(admin.ModelAdmin):
    list_display = ("label", "description", "created", "updated")
    search_fields = ("label", "description")
    ordering = ("-created_at",)
    readonly_fields = ("created", "updated")

    def created(self, obj):
        return obj.created_at
    created.admin_order_field = "created_at"
    created.short_description = "Créé le"

    def updated(self, obj):
        return obj.updated_at
    updated.admin_order_field = "updated_at"
    updated.short_description = "Mis à jour le"
