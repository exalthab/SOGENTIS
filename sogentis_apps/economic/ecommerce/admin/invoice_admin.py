from django.contrib import admin
from ..models.invoice import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("uuid", "order", "created_at")
    readonly_fields = ("uuid", "created_at", "file")
