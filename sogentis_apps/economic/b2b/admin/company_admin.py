# economic/b2b/admin/company_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_active", "created_at")
    search_fields = ("name", "email")
    list_filter = ("is_active",)
    ordering = ("name",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (_("Entreprise"), {"fields": ("name", "email", "is_active")}),
        (_("Dates"), {"fields": ("created_at",)}),
    )
