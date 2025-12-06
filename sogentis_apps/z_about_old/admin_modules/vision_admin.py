#about/admin_modules/value_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from z_about_old.models import VisionItem


@admin.register(VisionItem)
class VisionItemAdmin(TranslatableAdmin):
    """
    Administration des visions de l’organisation.
    """
    list_display = ("get_title", "icon", "image_preview", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("translations__title", "translations__description")
    ordering = ("order",)
    readonly_fields = ("image_preview", "created_at", "updated_at")

    fieldsets = (
        (_("Contenu"), {
            "fields": ("about_page", "title", "description"),
        }),
        (_("Apparence"), {
            "fields": ("icon", "image", "image_preview"),
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
        """Retourne le titre traduit."""
        return obj.safe_translation_getter("title", any_language=True)
    get_title.short_description = _("Titre")

    def image_preview(self, obj):
        """Affiche un aperçu de l'image liée."""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;">',
                obj.image.url
            )
        return "—"
    image_preview.short_description = _("Aperçu image")





# #about/admin_modules/vision_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from django.utils.html import format_html
# from parler.admin import TranslatableAdmin
# from about.models.vision_item import VisionItem


# @admin.register(VisionItem)
# class VisionItemAdmin(TranslatableAdmin):
#     list_display = ("get_title", "icon", "image_preview", "order")
#     search_fields = ("translations__title", "translations__description")
#     list_filter = ("order",)
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     fieldsets = (
#         (_("Informations générales"), {
#             "fields": ("about_page", "title", "description", "icon", "image", "image_preview", "order", "is_active"),
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = _("Titre")

#     def image_preview(self, obj):
#         if getattr(obj, "image", None):
#             try:
#                 return format_html(
#                     '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;">',
#                     obj.image.url
#                 )
#             except ValueError:
#                 return "—"
#         return "—"
#     image_preview.short_description = _("Aperçu image")
