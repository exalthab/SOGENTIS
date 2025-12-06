# about/admin_modules/section_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from z_about_old.models import AboutSection


@admin.register(AboutSection)
class AboutSectionAdmin(TranslatableAdmin):
    """
    Administration des sections dynamiques de la page À propos (Mission, Vision, Valeurs...).
    """
    list_display = ("get_title", "section_type", "order", "image_preview", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("section_type", "is_active")
    search_fields = ("translations__title", "translations__content")
    ordering = ("order",)
    readonly_fields = ("image_preview", "created_at", "updated_at")

    fieldsets = (
        (_("Contenu"), {
            "fields": ("title", "content", "section_type"),
        }),
        (_("Image"), {
            "fields": ("image", "image_preview"),
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
        """Retourne le titre traduit ou un fallback."""
        return obj.safe_translation_getter("title", any_language=True) or f"Section #{obj.id}"
    get_title.short_description = _("Titre")

    def image_preview(self, obj):
        """Affiche un aperçu de l'image si elle existe."""
        if getattr(obj, "image", None):
            try:
                return format_html(
                    '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;">',
                    obj.image.url
                )
            except ValueError:
                return "—"
        return "—"
    image_preview.short_description = _("Aperçu image")






# #about/admin_modules/section_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models import AboutSection


# @admin.register(AboutSection)
# class AboutSectionAdmin(TranslatableAdmin):
#     """
#     Administration des sections dynamiques de la page À propos (Mission, Vision, Valeurs...).
#     """
#     list_display = ("get_title", "section_type", "order", "image_preview", "is_active")
#     list_editable = ("order", "is_active")
#     list_filter = ("section_type", "is_active")
#     search_fields = ("translations__title", "translations__content")
#     ordering = ("order",)
#     readonly_fields = ("image_preview", "created_at", "updated_at")

#     fieldsets = (
#         (_("Contenu"), {
#             "fields": ("about_page", "title", "content", "section_type"),
#         }),
#         (_("Image"), {
#             "fields": ("image", "image_preview"),
#         }),
#         (_("Organisation"), {
#             "fields": ("order", "is_active"),
#         }),
#         (_("Métadonnées"), {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         """Retourne le titre traduit ou un fallback."""
#         return obj.safe_translation_getter("title", any_language=True) or f"Section #{obj.id}"
#     get_title.short_description = _("Titre")

#     def image_preview(self, obj):
#         """Affiche un aperçu de l'image si elle existe."""
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






# #about/admin_modules/section_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.about_section import AboutSection

# @admin.register(AboutSection)
# class AboutSectionAdmin(TranslatableAdmin):
#     list_display = ("get_title", "section_type", "order", "image_preview")
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         ("Contenu", {"fields": ("title", "content", "section_type")}),
#         ("Image", {"fields": ("image",)}),
#         ("Ordre & Dates", {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="70"/>', obj.image.url)
#         return "Pas d’image"
#     image_preview.short_description = "Image"


# @admin.register(AboutSection)
# class AboutSectionAdmin(TranslatableAdmin):
#     list_display = ("get_title", "order", "is_active")
#     list_editable = ("order", "is_active")
#     search_fields = ("translations__title",)
#     ordering = ("order",)

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"

    # def preview_image(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" width="70" height="70" style="border-radius:8px;object-fit:cover;"/>', obj.image.url)
    #     return _("Aucune image")
    # preview_image.short_description = _("Aperçu")
