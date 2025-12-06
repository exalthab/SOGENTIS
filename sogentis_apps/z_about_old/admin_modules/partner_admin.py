#about/admin_modules/partner_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from z_about_old.models import Partner


@admin.register(Partner)
class PartnerAdmin(TranslatableAdmin):
    """
    Administration des partenaires de l'organisation.
    """
    list_display = ("get_name", "website_link", "logo_preview", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("translations__name", "translations__description", "website")
    ordering = ("order",)
    readonly_fields = ("logo_preview", "created_at", "updated_at")

    fieldsets = (
        (_("Informations générales"), {
            "fields": ("name", "description", "logo", "logo_preview", "website"),
        }),
        (_("Organisation"), {
            "fields": ("order", "is_active"),
        }),
        (_("Métadonnées"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def get_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)
    get_name.short_description = _("Nom")

    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return "—"
    website_link.short_description = _("Site web")

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" style="object-fit:contain;border-radius:4px;">', obj.logo.url)
        return "—"
    logo_preview.short_description = _("Aperçu logo")





# # about/admin_modules/partner_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.partner import Partner



# @admin.register(Partner)
# class PartnerAdmin(TranslatableAdmin):
#     list_display = ("get_name", "website_link", "logo_preview", "order")
#     search_fields = ("translations__name", "website")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         ("Informations", {"fields": ("name", "website", "logo")}),
#         ("Ordre & Dates", {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def website_link(self, obj):
#         if obj.website:
#             return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
#         return "Aucun site"
#     website_link.short_description = "Site web"

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html('<img src="{}" width="70" style="object-fit:contain;"/>', obj.logo.url)
#         return "Pas de logo"
#     logo_preview.short_description = "Logo"

#     def get_name(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)
#     get_name.short_description = _("Nom")




# @admin.register(Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ("name", "website_link", "logo_preview", "order", "is_active")
#     search_fields = ("name", "website", "Translations__name",)
#     ordering = ("order",)
#     list_editable = ("order", "is_active")
#     readonly_fields = ("created_at", "order")

#     def website_link(self, obj):
#         if obj.website:
#             return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
#         return _("Aucun site")
#     website_link.short_description = _("Site web")

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html('<img src="{}" width="70" height="70" style="object-fit:contain;"/>', obj.logo.url)
#         return _("Pas de logo")
#     logo_preview.short_description = _("Logo")

#     def get_name(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)
#     get_name.short_description = _("Nom")
