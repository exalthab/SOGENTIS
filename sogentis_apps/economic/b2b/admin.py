# economic/b2b/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Company,
    CompanyUser,
    BulkOrder,
    BulkOrderItem,
    Invoice,
    RFQ,
    Offer,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "is_active", "owner", "created_at")
    list_filter = ("status", "is_active")
    search_fields = ("name", "email", "phone", "city")
    autocomplete_fields = ("owner",)


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "user__username", "company__name")
    autocomplete_fields = ("user", "company")


class BulkOrderItemInline(admin.TabularInline):
    model = BulkOrderItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(BulkOrder)
class BulkOrderAdmin(admin.ModelAdmin):
    list_display = ("uuid", "company", "status", "total_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("uuid", "reference", "company__name")
    autocomplete_fields = ("company",)
    inlines = (BulkOrderItemInline,)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "bulk_order", "status", "amount", "issued_at", "paid_at")
    list_filter = ("status",)
    search_fields = ("invoice_number", "bulk_order__uuid", "bulk_order__company__name")
    autocomplete_fields = ("bulk_order",)


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "status", "deadline", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "company__name", "created_by__email")
    autocomplete_fields = ("company", "created_by")


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("rfq", "supplier", "status", "price_total", "currency", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("rfq__title", "supplier__email")
    autocomplete_fields = ("rfq", "supplier")


admin.site.site_header = "SOGENTIS — Admin Économique (B2B)"
admin.site.site_title = "SOGENTIS Admin"



# # economic/b2b/admin.py
# from django.contrib import admin

# # Admins modulaires (si présents)
# from .admin.invoice_admin import *      # noqa
# from .admin.bulk_order_admin import *   # noqa

# from .models import Company, CompanyUser


# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ("name", "email", "is_active", "created_at")
#     search_fields = ("name", "email")
#     list_filter = ("is_active",)


# @admin.register(CompanyUser)
# class CompanyUserAdmin(admin.ModelAdmin):
#     list_display = ("user", "company", "role", "is_active", "created_at")
#     list_filter = ("role", "is_active")
#     search_fields = ("user__email", "user__username", "company__name")


# admin.site.site_header = "SOGENTIS — Admin Économique (B2B)"
# admin.site.site_title = "SOGENTIS Admin"





# # /economic/b2b/admin.py
# from django.contrib import admin

# # 🔗 Pont vers les admins modulaires
# from .admin.invoice_admin import *      # noqa
# from .admin.bulk_order_admin import *   # noqa

# from .models.company import Company
# from .models.company_user import CompanyUser


# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ("name", "email", "is_active", "created_at")
#     search_fields = ("name", "email")
#     list_filter = ("is_active",)


# @admin.register(CompanyUser)
# class CompanyUserAdmin(admin.ModelAdmin):
#     list_display = ("user", "company", "role", "is_active")
#     list_filter = ("role", "is_active")
#     search_fields = ("user__username", "company__name")


# admin.site.site_header = "SOGENTIS — Admin Économique (B2B)"
# admin.site.site_title = "SOGENTIS Admin"
