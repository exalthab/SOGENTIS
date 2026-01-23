# economic/services/admin/quote_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.services.models import Quote, QuoteLine


class QuoteLineInline(admin.TabularInline):
    model = QuoteLine
    extra = 1
    fields = (
        "order",
        "service",
        "package",
        "title_override",
        "quantity",
        "unit_price",
        "discount_rate",
    )
    ordering = ("order", "id")
    autocomplete_fields = ("service", "package")


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "quote_number",
        "status",
        "currency",
        "total",
        "client_name",
        "client_email",
        "valid_until",
        "created_at",
    )
    list_filter = ("status", "currency", "is_active", "source", "created_at")
    search_fields = (
        "quote_number",
        "client_name",
        "client_email",
        "client_phone",
        "company_name",
        "subject",
    )
    ordering = ("-created_at", "-id")

    readonly_fields = (
        "public_id",
        "quote_number",
        "subtotal",
        "discount_total",
        "tax_total",
        "total",
        "created_at",
        "updated_at",
    )

    inlines = [QuoteLineInline]

    fieldsets = (
        (_("Identifiants"), {"fields": ("public_id", "quote_number", "status", "source", "is_active")}),
        (_("Client"), {"fields": ("client_name", "company_name", "client_email", "client_phone")}),
        (_("Adresse"), {"fields": ("country", "city", "address")}),
        (_("Objet & contenu"), {"fields": ("subject", "message")}),
        (_("Conditions"), {"fields": ("terms",)}),
        (_("Notes internes"), {"fields": ("internal_notes",), "classes": ("collapse",)}),
        (_("Tarification"), {"fields": ("currency", "tax_rate")}),
        (_("Totaux"), {"fields": ("subtotal", "discount_total", "tax_total", "total")}),
        (_("Dates"), {"fields": ("issued_at", "valid_until")}),
        (_("Système"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ("mark_sent", "mark_accepted", "mark_rejected", "mark_cancelled", "recalculate_totals")

    @admin.action(description=_("Marquer comme envoyé"))
    def mark_sent(self, request, queryset):
        for q in queryset:
            q.mark_sent()

    @admin.action(description=_("Marquer comme accepté"))
    def mark_accepted(self, request, queryset):
        for q in queryset:
            q.mark_accepted()

    @admin.action(description=_("Marquer comme refusé"))
    def mark_rejected(self, request, queryset):
        for q in queryset:
            q.mark_rejected()

    @admin.action(description=_("Marquer comme annulé"))
    def mark_cancelled(self, request, queryset):
        for q in queryset:
            q.mark_cancelled()

    @admin.action(description=_("Recalculer les totaux"))
    def recalculate_totals(self, request, queryset):
        for q in queryset:
            q.recalculate(save=True)


@admin.register(QuoteLine)
class QuoteLineAdmin(admin.ModelAdmin):
    list_display = ("quote", "display_title", "quantity", "unit_price", "discount_rate", "order", "created_at")
    list_filter = ("created_at",)
    search_fields = ("quote__quote_number", "title_override")
    ordering = ("-created_at", "-id")
    autocomplete_fields = ("quote", "service", "package")
    readonly_fields = ("created_at", "updated_at")
