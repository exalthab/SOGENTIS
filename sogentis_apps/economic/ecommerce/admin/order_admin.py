# sogentis_apps/economic/ecommerce/admin/order_admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "unit_price")
    autocomplete_fields = ("product",)
    show_change_link = True


@admin.action(description=_("Marquer comme payée"))
def mark_paid(modeladmin, request, queryset):
    queryset.update(status="paid")


@admin.action(description=_("Marquer comme expédiée"))
def mark_shipped(modeladmin, request, queryset):
    queryset.update(status="shipped")


@admin.action(description=_("Marquer comme terminée"))
def mark_completed(modeladmin, request, queryset):
    queryset.update(status="completed")


@admin.action(description=_("Annuler"))
def mark_cancelled(modeladmin, request, queryset):
    queryset.update(status="cancelled")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = ("id", "uuid", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("uuid", "user__email", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at")

    actions = [
        mark_paid,
        mark_shipped,
        mark_completed,
        mark_cancelled,
    ]

    fieldsets = (
        (_("Client"), {"fields": ("user",)}),
        (_("Commande"), {"fields": ("uuid", "status", "total_amount")}),
        (_("Dates"), {"fields": ("created_at",)}),
    )
