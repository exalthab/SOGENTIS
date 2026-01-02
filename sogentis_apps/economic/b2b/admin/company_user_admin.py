# economic/b2b/admin/company_user_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import CompanyUser


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "is_active", "created_at")
    search_fields = ("user__email", "user__username", "company__name")
    list_filter = ("role", "is_active", "company")
    readonly_fields = ("created_at",)
    fieldsets = (
        (_("Utilisateur"), {"fields": ("user", "company", "role", "is_active")}),
        (_("Dates"), {"fields": ("created_at",)}),
    )
