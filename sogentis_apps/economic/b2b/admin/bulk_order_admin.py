# economic/b2b/admin/bulk_order_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from economic.b2b.models.bulk_order import BulkOrder
from economic.b2b.models.bulk_order_item import BulkOrderItem
from economic.b2b.services.invoice_service import create_invoice_for_bulk_order


class BulkOrderItemInline(admin.TabularInline):
    model = BulkOrderItem
    extra = 0
    autocomplete_fields = ("product",)
    readonly_fields = ("total_price",)


@admin.action(description=_("Passer en 'Soumise'"))
def mark_submitted(modeladmin, request, queryset):
    queryset.update(status="submitted")


@admin.action(description=_("Approuver"))
def mark_approved(modeladmin, request, queryset):
    queryset.update(status="approved")


@admin.action(description=_("Rejeter"))
def mark_rejected(modeladmin, request, queryset):
    queryset.update(status="rejected")


@admin.action(description=_("Générer facture (si absente)"))
def generate_invoice(modeladmin, request, queryset):
    for order in queryset.select_related("company"):
        if hasattr(order, "invoice"):
            continue
        with transaction.atomic():
            create_invoice_for_bulk_order(order)


@admin.register(BulkOrder)
class BulkOrderAdmin(admin.ModelAdmin):
    inlines = [BulkOrderItemInline]

    list_display = ("uuid", "company", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("uuid", "company__name", "reference")
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at", "updated_at", "total_amount")

    actions = (mark_submitted, mark_approved, mark_rejected, generate_invoice)

    fieldsets = (
        (_("Entreprise"), {"fields": ("company",)}),
        (_("Commande"), {"fields": ("uuid", "status", "total_amount", "reference")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
        (_("Notes"), {"fields": ("notes",)}),
    )









# # /economic/b2b/admin/bulk_order_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models.bulk_order import BulkOrder
# from economic.b2b.models.bulk_order_item import BulkOrderItem


# class BulkOrderItemInline(admin.TabularInline):
#     model = BulkOrderItem
#     extra = 0
#     autocomplete_fields = ("product",)
#     readonly_fields = ("total_price",)


# @admin.register(BulkOrder)
# class BulkOrderAdmin(admin.ModelAdmin):
#     inlines = [BulkOrderItemInline]

#     list_display = ("uuid", "company", "status", "total_amount", "created_at")
#     list_filter = ("status", "created_at")
#     search_fields = ("uuid", "company__name")
#     ordering = ("-created_at",)
#     readonly_fields = ("uuid", "created_at", "updated_at", "total_amount")

#     fieldsets = (
#         (_("Entreprise"), {"fields": ("company",)}),
#         (_("Commande"), {"fields": ("uuid", "status", "total_amount", "reference")}),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#         (_("Notes"), {"fields": ("notes",)}),
#     )
