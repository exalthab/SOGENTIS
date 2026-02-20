# economic/prestations/admin/prestations_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.prestations.models import Prestation, PrestationFeature


class PrestationFeatureInline(admin.TabularInline):
    model = PrestationFeature
    extra = 1
    fields = ("label", "order")
    ordering = ("order", "id")


@admin.register(Prestation)
class PrestationAdmin(TranslatableAdmin):
    list_display = (
        "title_col",
        "prestation_type",
        "deliverable",
        "category",
        "base_price",
        "turnaround_days",
        "is_active",
        "is_featured",
        "order",
        "updated_at",
    )
    list_filter = (
        "category",
        "prestation_type",
        "deliverable",
        "is_active",
        "is_featured",
    )
    search_fields = (
        "translations__title",
        "translations__short_description",
        "slug",
    )
    ordering = ("order", "-is_featured", "-created_at", "-id")
    inlines = [PrestationFeatureInline]

    fieldsets = (
        (_("Identité"), {"fields": ("title", "slug", "category", "icon")}),
        (_("Type & livrable"), {"fields": ("prestation_type", "deliverable")}),
        (_("Prix & délai"), {"fields": ("base_price", "turnaround_days")}),
        (_("Contenu"), {"fields": ("short_description", "description")}),
        (_("SEO"), {"fields": ("seo_title", "seo_description")}),
        (_("Affichage"), {"fields": ("order", "is_featured")}),
        (_("Publication"), {"fields": ("is_active", "published_at")}),
        (_("Système"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    actions = ("activate", "deactivate", "mark_featured", "unmark_featured")

    @admin.display(description=_("Titre"))
    def title_col(self, obj: Prestation) -> str:
        return obj.safe_translation_getter("title", any_language=True) or f"Prestation #{obj.pk}"

    @admin.action(description=_("Activer les prestations sélectionnées"))
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_("Désactiver les prestations sélectionnées"))
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description=_("Mettre en avant"))
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description=_("Retirer la mise en avant"))
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)






# # economic/prestations/admin/prestations_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.prestations.models import Service, ServiceFeature


# class ServiceFeatureInline(admin.TabularInline):
#     model = ServiceFeature
#     extra = 1
#     fields = ("label", "order")
#     ordering = ("order", "id")


# @admin.register(Service)
# class ServiceAdmin(TranslatableAdmin):
#     list_display = (
#         "title_col",
#         "service_type",
#         "deliverable",
#         "category",
#         "base_price",
#         "turnaround_days",
#         "is_active",
#         "is_featured",
#         "order",
#         "updated_at",
#     )
#     list_filter = (
#         "category",
#         "service_type",
#         "deliverable",
#         "is_active",
#         "is_featured",
#     )
#     search_fields = (
#         "translations__title",
#         "translations__short_description",
#         "slug",
#     )
#     ordering = ("order", "-is_featured", "-created_at", "-id")
#     inlines = [ServiceFeatureInline]

#     fieldsets = (
#         (_("Identité"), {"fields": ("title", "slug", "category", "icon")}),
#         (_("Type & livrable"), {"fields": ("service_type", "deliverable")}),
#         (_("Prix & délai"), {"fields": ("base_price", "turnaround_days")}),
#         (_("Contenu"), {"fields": ("short_description", "description")}),
#         (_("SEO"), {"fields": ("seo_title", "seo_description")}),
#         (_("Affichage"), {"fields": ("order", "is_featured")}),
#         (_("Publication"), {"fields": ("is_active", "published_at")}),
#         (_("Système"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )

#     readonly_fields = ("created_at", "updated_at")

#     actions = ("activate", "deactivate", "mark_featured", "unmark_featured")

#     @admin.display(description=_("Titre"))
#     def title_col(self, obj: Service) -> str:
#         return obj.safe_translation_getter("title", any_language=True) or f"Service #{obj.pk}"

#     @admin.action(description=_("Activer les services sélectionnés"))
#     def activate(self, request, queryset):
#         queryset.update(is_active=True)

#     @admin.action(description=_("Désactiver les services sélectionnés"))
#     def deactivate(self, request, queryset):
#         queryset.update(is_active=False)

#     @admin.action(description=_("Mettre en avant"))
#     def mark_featured(self, request, queryset):
#         queryset.update(is_featured=True)

#     @admin.action(description=_("Retirer la mise en avant"))
#     def unmark_featured(self, request, queryset):
#         queryset.update(is_featured=False)






# # # economic/services/admin/service_admin.py-new
# from __future__ import annotations

# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from economic.services.models import Service, ServiceFeature


# class ServiceFeatureInline(admin.TabularInline):
#     model = ServiceFeature
#     extra = 1
#     fields = ("label", "order")
#     ordering = ("order", "id")


# @admin.register(Service)
# class ServiceAdmin(TranslatableAdmin):
#     list_display = ("code", "category", "is_published", "is_featured", "order", "updated_at")
#     list_filter = ("category", "is_published", "is_featured")
#     search_fields = ("code", "translations__name", "translations__slug")
#     ordering = ("order", "-is_featured", "id")
#     inlines = [ServiceFeatureInline]

#     fieldsets = (
#         ("Identité", {"fields": ("code", "category", "icon")}),
#         ("Affichage", {"fields": ("order", "is_featured")}),
#         ("Publication", {"fields": ("is_published", "published_at")}),
#         ("Traductions", {"fields": ("name", "slug", "short_description", "description")}),
#         ("SEO", {"fields": ("seo_title", "seo_description")}),
#         ("Système", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )
#     readonly_fields = ("created_at", "updated_at")

#     actions = ("publish", "unpublish")

#     @admin.action(description="Publier les services sélectionnés")
#     def publish(self, request, queryset):
#         queryset.update(is_published=True)

#     @admin.action(description="Dépublier les services sélectionnés")
#     def unpublish(self, request, queryset):
#         queryset.update(is_published=False)






# # economic/services/admin/service_admin.py-existant
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.services.models import Service


# @admin.register(Service)
# class ServiceAdmin(TranslatableAdmin):
#     list_display = ("title_col", "category", "base_price", "is_active", "is_featured", "created_at")
#     list_filter = ("is_active", "is_featured", "category")
#     search_fields = ("translations__title", "slug")
#     autocomplete_fields = ("category",)
#     ordering = ("-created_at", "-id")

#     def title_col(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)

#     title_col.short_description = _("Titre")







# # economic/services/admin/service_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from ..models import Service


# @admin.register(Service)
# class ServiceAdmin(TranslatableAdmin):
#     list_display = (
#         "title_col",
#         "category",
#         "base_price",
#         "is_active",
#         "is_featured",
#         "created_at",
#     )
#     list_filter = ("is_active", "is_featured", "category")
#     search_fields = ("translations__title", "slug")

#     def title_col(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)

#     title_col.short_description = _("Titre")
