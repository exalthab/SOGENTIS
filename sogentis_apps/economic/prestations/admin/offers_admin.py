# economic/prestations/admin/offers_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import PackageOffer, PrestationPlan


@admin.register(PrestationPlan)
class PrestationPlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "prestation",
        "title",
        "price",
        "currency",
        "allow_online_payment",
        "delivery_mode",
        "is_active",
        "is_featured",
        "order",
        "updated_at",
    )
    list_filter = ("is_active", "is_featured", "allow_online_payment", "delivery_mode", "currency")
    search_fields = ("title", "slug", "prestation__slug", "prestation__title", "prestation__name")
    autocomplete_fields = ("prestation",)
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-is_featured", "order", "-updated_at", "-id")

    fieldsets = (
        (_("Cible"), {"fields": ("prestation",)}),
        (_("Contenu"), {"fields": ("title", "slug", "subtitle", "short_description", "description")}),
        (_("Tarification"), {"fields": ("price", "currency", "allow_online_payment")}),
        (_("Preview & Livrables"), {"fields": ("preview_label", "preview_url", "delivery_mode", "deliverable_file", "deliverable_url", "deliverable_notes")}),
        (_("Publication"), {"fields": ("is_active", "is_featured", "order")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(PackageOffer)
class PackageOfferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "package",
        "title",
        "price",
        "currency",
        "allow_online_payment",
        "delivery_mode",
        "is_active",
        "is_featured",
        "order",
        "updated_at",
    )
    list_filter = ("is_active", "is_featured", "allow_online_payment", "delivery_mode", "currency")
    search_fields = ("title", "slug", "package__slug", "package__title", "package__name")
    autocomplete_fields = ("package",)
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-is_featured", "order", "-updated_at", "-id")

    fieldsets = (
        (_("Cible"), {"fields": ("package",)}),
        (_("Contenu"), {"fields": ("title", "slug", "subtitle", "short_description", "description")}),
        (_("Tarification"), {"fields": ("price", "currency", "allow_online_payment")}),
        (_("Preview & Livrables"), {"fields": ("preview_label", "preview_url", "delivery_mode", "deliverable_file", "deliverable_url", "deliverable_notes")}),
        (_("Publication"), {"fields": ("is_active", "is_featured", "order")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
