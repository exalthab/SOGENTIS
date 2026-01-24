# economic/ecommerce/admin/invoice_admin.py
from __future__ import annotations

from django.contrib import admin

from economic.ecommerce.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("uuid", "order", "created_at")
    readonly_fields = ("uuid", "created_at", "file")
    ordering = ("-created_at",)
    autocomplete_fields = ("order",)
    search_fields = ("uuid", "order__uuid")





# # /economic/ecommerce/admin/invoice_admin.py
# from django.contrib import admin
# from ..models.invoice import Invoice


# @admin.register(Invoice)
# class InvoiceAdmin(admin.ModelAdmin):
#     list_display = ("uuid", "order", "created_at")
#     readonly_fields = ("uuid", "created_at", "file")
