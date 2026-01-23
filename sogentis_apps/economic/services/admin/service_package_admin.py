# economic/services/admin/service_package_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.services.models import ServicePackage, ServicePackageFeature


class ServicePackageFeatureInline(admin.TabularInline):
    model = ServicePackageFeature
    extra = 1
    fields = ("label", "is_highlight", "order")
    ordering = ("order", "id")


@admin.register(ServicePackage)
class ServicePackageAdmin(TranslatableAdmin):
    list_display = (
        "name_col",
        "tier",
        "billing_period",
        "total_price",
        "currency",
        "is_active",
        "is_featured",
        "order",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "tier", "billing_period", "currency", "support_level")
    search_fields = ("translations__name", "translations__tagline", "slug")
    ordering = ("order", "-is_featured", "-created_at", "-id")

    filter_horizontal = ("services",)
    inlines = [ServicePackageFeatureInline]

    fieldsets = (
        (_("Identité"), {"fields": ("name", "slug", "tagline")}),
        (_("Prix & Périodicité"), {"fields": ("total_price", "currency", "billing_period", "tier")}),
        (_("Services inclus"), {"fields": ("services",)}),
        (_("Options du pack"), {"fields": ("included_domain_year", "included_ssl", "emails_count", "max_pages")}),
        (_("Support"), {"fields": ("support_level",)}),
        (_("CTA & SEO"), {"fields": ("cta_label", "seo_title", "seo_description")}),
        (_("Affichage"), {"fields": ("order", "is_featured")}),
        (_("Statut"), {"fields": ("is_active",)}),
        (_("Système"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    actions = ("activate", "deactivate", "mark_featured", "unmark_featured")

    @admin.display(description=_("Nom du pack"))
    def name_col(self, obj: ServicePackage) -> str:
        return obj.safe_translation_getter("name", any_language=True) or f"Pack #{obj.pk}"

    @admin.action(description=_("Activer les packs sélectionnés"))
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_("Désactiver les packs sélectionnés"))
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description=_("Mettre en avant"))
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description=_("Retirer la mise en avant"))
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)





# # economic/services/admin/service_package_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.services.models import ServicePackage, ServicePackageFeature


# class ServicePackageFeatureInline(admin.TabularInline):
#     model = ServicePackageFeature
#     extra = 1
#     fields = ("label", "is_highlight", "order")
#     ordering = ("order", "id")


# @admin.register(ServicePackage)
# class ServicePackageAdmin(TranslatableAdmin):
#     """
#     Admin PROD pour ServicePackage :
#     - Compatible avec ton modèle existant (Parler)
#     - M2M services
#     - Inlines des features (bullet list)
#     - Champs pack prod ajoutés (tier/billing/currency/support/...)
#     - Actions publish/unpublish basées sur is_active (ton champ)
#     """

#     list_display = (
#         "name_col",
#         "tier",
#         "billing_period",
#         "total_price",
#         "currency",
#         "is_active",
#         "is_featured",
#         "order",
#         "created_at",
#     )
#     list_filter = ("is_active", "is_featured", "tier", "billing_period", "currency", "support_level")
#     search_fields = ("translations__name", "translations__tagline", "slug")
#     ordering = ("order", "-is_featured", "-created_at", "-id")

#     filter_horizontal = ("services",)
#     inlines = [ServicePackageFeatureInline]

#     fieldsets = (
#         (_("Identité"), {"fields": ("name", "slug", "tagline")}),
#         (_("Prix & Périodicité"), {"fields": ("total_price", "currency", "billing_period", "tier")}),
#         (_("Services inclus"), {"fields": ("services",)}),
#         (_("Options du pack"), {"fields": ("included_domain_year", "included_ssl", "emails_count", "max_pages")}),
#         (_("Support"), {"fields": ("support_level",)}),
#         (_("CTA & SEO"), {"fields": ("cta_label", "seo_title", "seo_description")}),
#         (_("Affichage"), {"fields": ("order", "is_featured")}),
#         (_("Statut"), {"fields": ("is_active",)}),
#         (_("Système"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )

#     readonly_fields = ("created_at", "updated_at")

#     actions = ("activate", "deactivate")

#     @admin.display(description=_("Nom du pack"))
#     def name_col(self, obj: ServicePackage) -> str:
#         return obj.safe_translation_getter("name", any_language=True) or f"Pack #{obj.pk}"

#     @admin.action(description=_("Activer les packs sélectionnés"))
#     def activate(self, request, queryset):
#         queryset.update(is_active=True)

#     @admin.action(description=_("Désactiver les packs sélectionnés"))
#     def deactivate(self, request, queryset):
#         queryset.update(is_active=False)




# # economic/services/admin/service_package_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from ..models import ServicePackage


# @admin.register(ServicePackage)
# class ServicePackageAdmin(TranslatableAdmin):
#     list_display = ("name_col", "total_price", "is_active", "created_at")
#     list_filter = ("is_active",)
#     filter_horizontal = ("services",)
#     search_fields = ("translations__name", "slug")

#     def name_col(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)

#     name_col.short_description = _("Nom du pack")
