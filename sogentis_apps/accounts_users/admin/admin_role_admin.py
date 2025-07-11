# accounts_users/admin/admin_role_admin.py

from django.contrib import admin
from accounts_users.models import AdminRole


@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
