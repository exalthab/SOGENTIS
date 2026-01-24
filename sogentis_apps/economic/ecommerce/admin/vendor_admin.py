# economic/ecommerce/admin/vendor_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Vendor


@admin.action(description=_("Vérifier les vendeurs sélectionnés"))
def verify_vendors(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.action(description=_("Retirer la vérification"))
def unverify_vendors(modeladmin, request, queryset):
    queryset.update(is_verified=False)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "user", "is_verified", "created_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("company_name", "user__email", "user__phone", "user__first_name", "user__last_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)

    actions = [verify_vendors, unverify_vendors]

    fieldsets = (
        (_("Identité"), {"fields": ("user", "company_name")}),
        (_("Statut"), {"fields": ("is_verified",)}),
        (_("Dates"), {"fields": ("created_at",)}),
    )





# # /economic/ecommerce/admin/vendor_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Vendor


# @admin.action(description=_("Vérifier les vendeurs sélectionnés"))
# def verify_vendors(modeladmin, request, queryset):
#     queryset.update(is_verified=True)


# @admin.action(description=_("Retirer la vérification"))
# def unverify_vendors(modeladmin, request, queryset):
#     queryset.update(is_verified=False)


# @admin.register(Vendor)
# class VendorAdmin(admin.ModelAdmin):
#     list_display = ("id", "company_name", "user", "is_verified", "created_at")
#     list_filter = ("is_verified", "created_at")
#     search_fields = ("company_name", "user__email", "user__username")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)

#     actions = [verify_vendors, unverify_vendors]

#     fieldsets = (
#         (_("Identité"), {"fields": ("user", "company_name")}),
#         (_("Statut"), {"fields": ("is_verified",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )
