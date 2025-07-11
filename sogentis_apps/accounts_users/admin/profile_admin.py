# accounts_users/admin/profile_admin.py

from django.contrib import admin
from accounts_users.models.users_profile import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", 
        "full_name", 
        "phone", 
        "country", 
        "created", 
        "updated",
        
    )
    search_fields = ("full_name", "phone", "country", "user__email")
    list_filter = ("country", "membership_role")
    readonly_fields = ("created", "updated")

    def created(self, obj):
        return obj.created_at
    created.admin_order_field = "created_at"
    created.short_description = "Créé le"

    def updated(self, obj):
        return obj.updated_at
    updated.admin_order_field = "updated_at"
    updated.short_description = "Mis à jour le"
