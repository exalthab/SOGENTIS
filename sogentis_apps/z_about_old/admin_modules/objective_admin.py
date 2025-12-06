#about/admin_modules/objective_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from z_about_old.models import ObjectiveItem


@admin.register(ObjectiveItem)
class ObjectiveItemAdmin(TranslatableAdmin):
    """
    Administration des objectifs affichés dans la page À propos.
    """
    list_display = ("get_title", "icon", "image_preview", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("translations__title", "translations__description")
    list_filter = ("is_active",)
    ordering = ("order",)
    readonly_fields = ("image_preview", "created_at", "updated_at")

    fieldsets = (
        (_("Informations générales"), {
            "fields": ("about_page", "title", "description", "icon", "image", "image_preview"),
        }),
        (_("Organisation"), {
            "fields": ("order", "is_active"),
        }),
        (_("Métadonnées"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def get_title(self, obj):
        return obj.safe_translation_getter("title", any_language=True)
    get_title.short_description = _("Titre")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;">',
                obj.image.url
            )
        return "—"
    image_preview.short_description = _("Aperçu image")




# #about/admin_modules/objective_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.objective_item import ObjectiveItem

# @admin.register(ObjectiveItem)
# class ObjectiveItemAdmin(TranslatableAdmin):
#     list_display = ("get_title", "is_active", "order", "created_at")
#     list_editable = ("is_active", "order")
#     search_fields = ("translations__title", "description")
#     list_filter = ("is_active",)
#     ordering = ("order",)
#     readonly_fields = ("created_at", "updated_at")


#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = _("Titre")