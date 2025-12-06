#about/admin_modules/mother_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from z_about_old.models import Mother


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    """
    Administration des mamans bénéficiaires.
    """
    list_display = ("name", "children_count", "photo_preview", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("name", "story")
    readonly_fields = ("photo_preview", "created_at", "updated_at")
    ordering = ("name",)

    fieldsets = (
        (_("Informations générales"), {
            "fields": ("name", "children_count", "photo", "photo_preview", "story"),
        }),
        (_("Statut"), {
            "fields": ("is_active",),
        }),
        (_("Métadonnées"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;">', obj.photo.url)
        return "—"
    photo_preview.short_description = _("Aperçu photo")







# # about/admin_modules/mother_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.mother import Mother


# # @admin.register(Mother)
# class MotherAdmin(TranslatableAdmin):
#     list_display = ("get_name", "photo_preview", "is_active")
#     list_editable = ("is_active",)
#     search_fields = ("translations__name", "translations__profession")
#     readonly_fields = ("photo_preview",)

#     fieldsets = (
#         (_("Informations générales"), {
#             "fields": ("about_page", "name", "profession", "photo", "photo_preview", "story", "is_active"),
#         }),
#     )

#     def get_name(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)
#     get_name.short_description = _("Nom")

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;">', obj.photo.url)
#         return "—"
#     photo_preview.short_description = _("Aperçu photo")




# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from about.models.mother import Mother


# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "photo_preview", "created_at")
#     list_editable = ("is_active",)
#     list_filter = ("is_active",)
#     search_fields = ("name",)
#     readonly_fields = ("created_at", "updated_at")

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
#         return "Pas de photo"
#     photo_preview.short_description = "Photo"


# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "photo_preview", "created_at", "updated_at")
#     list_filter = ("is_active",)
#     search_fields = ("name", "registration_number")
#     list_editable = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
#         return _("Pas de photo")
#     photo_preview.short_description = _("Photo")
