# economic/prestations/admin/entitlements_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import PrestationEntitlement


@admin.register(PrestationEntitlement)
class PrestationEntitlementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "target_label",
        "status",
        "provider",
        "paid_amount",
        "paid_currency",
        "paid_at",
        "download_count",
        "download_limit",
        "expires_at",
        "created_at",
    )
    list_filter = ("status", "provider", "paid_currency")
    search_fields = (
        "user__email",
        "user__username",
        "provider_ref",
        "order_reference",
        "prestation_plan__slug",
        "package_offer__slug",
        "prestation__slug",
        "package__slug",
    )
    autocomplete_fields = ("user", "prestation_plan", "package_offer", "prestation", "package")
    readonly_fields = ("download_token", "created_at", "updated_at")

    fieldsets = (
        (_("Utilisateur"), {"fields": ("user",)}),
        (_("Cible (XOR)"), {"fields": ("prestation_plan", "package_offer", "prestation", "package")}),
        (_("Statut"), {"fields": ("status", "expires_at")}),
        (_("Paiement"), {"fields": ("provider", "provider_ref", "order_reference", "paid_amount", "paid_currency", "paid_at")}),
        (_("Téléchargements"), {"fields": ("download_token", "download_limit", "download_count")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("Cible"))
    def target_label(self, obj: PrestationEntitlement) -> str:
        if obj.prestation_plan_id:
            return f"PLAN: {obj.prestation_plan}"
        if obj.package_offer_id:
            return f"PACK OFFER: {obj.package_offer}"
        if obj.prestation_id:
            return f"PRESTATION: {obj.prestation}"
        if obj.package_id:
            return f"PACK: {obj.package}"
        return "—"
