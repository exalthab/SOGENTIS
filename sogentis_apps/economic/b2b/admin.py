from django.contrib import admin

# 🔗 Pont vers les admins modulaires
from .admin.invoice_admin import *      # noqa
from .admin.bulk_order_admin import *   # noqa

from .models.company import Company
from .models.company_user import CompanyUser


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_active", "created_at")
    search_fields = ("name", "email")
    list_filter = ("is_active",)


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "company__name")


admin.site.site_header = "SOGENTIS — Admin Économique (B2B)"
admin.site.site_title = "SOGENTIS Admin"
