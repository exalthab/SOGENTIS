# /economic/b2b/admin/invoice_admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from economic.b2b.models import Invoice


@admin.action(description=_("Marquer comme émise"))
def mark_issued(modeladmin, request, queryset):
    queryset.update(
        status="issued",
        issued_at=timezone.now(),
    )


@admin.action(description=_("Marquer comme payée"))
def mark_paid(modeladmin, request, queryset):
    queryset.update(
        status="paid",
        paid_at=timezone.now(),
    )


@admin.action(description=_("Annuler les factures"))
def mark_cancelled(modeladmin, request, queryset):
    queryset.update(status="cancelled")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "company",
        "status",
        "amount",
        "issued_at",
        "paid_at",
        "created_at",
    )

    list_filter = ("status", "created_at", "issued_at")
    search_fields = (
        "invoice_number",
        "bulk_order__company__name",
        "bulk_order__uuid",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "issued_at",
        "paid_at",
    )

    actions = [mark_issued, mark_paid, mark_cancelled]

    fieldsets = (
        (_("Commande"), {
            "fields": ("bulk_order",),
        }),
        (_("Facture"), {
            "fields": ("invoice_number", "status", "amount"),
        }),
        (_("Échéances"), {
            "fields": ("issued_at", "due_date", "paid_at"),
        }),
        (_("Notes"), {
            "fields": ("notes",),
        }),
        (_("Système"), {
            "fields": ("uuid", "created_at", "updated_at"),
        }),
    )

    def company(self, obj):
        return obj.bulk_order.company

    company.short_description = _("Entreprise")
