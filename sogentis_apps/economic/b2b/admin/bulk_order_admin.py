# /economic/b2b/admin/bulk_order_admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.b2b.models.bulk_order import BulkOrder
from economic.b2b.models.bulk_order_item import BulkOrderItem


class BulkOrderItemInline(admin.TabularInline):
    model = BulkOrderItem
    extra = 0
    autocomplete_fields = ("product",)
    readonly_fields = ("total_price",)


@admin.register(BulkOrder)
class BulkOrderAdmin(admin.ModelAdmin):
    inlines = [BulkOrderItemInline]

    list_display = ("uuid", "company", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("uuid", "company__name")
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at", "updated_at", "total_amount")

    fieldsets = (
        (_("Entreprise"), {"fields": ("company",)}),
        (_("Commande"), {"fields": ("uuid", "status", "total_amount", "reference")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
        (_("Notes"), {"fields": ("notes",)}),
    )
