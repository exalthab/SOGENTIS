#about/admin_modules/child_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from z_about_old.models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    """
    Administration des enfants bénéficiaires.
    """
    list_display = ("name", "age", "gender", "photo_preview", "sponsored", "is_active")
    list_filter = ("gender", "sponsored", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "school")
    readonly_fields = ("photo_preview", "created_at", "updated_at")
    ordering = ("name",)

    fieldsets = (
        (_("Informations générales"), {
            "fields": ("name", "gender", "age", "school", "photo", "photo_preview", "story"),
        }),
        (_("Statut"), {
            "fields": ("sponsored", "is_active"),
        }),
        (_("Métadonnées"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;">', obj.photo.url)
        return "—"
    photo_preview.short_description = _("Aperçu photo")







# # about/admin_modules/child_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.child import Child


# @admin.register(Child)
# class ChildAdmin(TranslatableAdmin):
#     list_display = ("get_name", "age", "gender", "photo_preview", "is_active")
#     list_editable = ("is_active",)
#     list_filter = ("gender", "is_active")
#     search_fields = ("translations__name",)
#     readonly_fields = ("photo_preview",)

#     fieldsets = (
#         (_("Informations générales"), {
#             "fields": ("about_page", "name", "age", "gender", "photo", "photo_preview", "story", "is_active"),
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
# from about.models.child import Child


# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ("name", "gender", "age", "school", "is_active", "photo_preview")
#     list_editable = ("is_active",)
#     list_filter = ("gender", "is_active")
#     search_fields = ("name", "school")
#     readonly_fields = ("created_at", "updated_at")

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
#         return "Pas de photo"
#     photo_preview.short_description = "Photo"
    
    
# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ("name", "gender", "age", "school", "is_active", "photo_preview")
#     list_filter = ("gender", "is_active")
#     search_fields = ("name", "registration_number", "school")
#     list_editable = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")

    # def photo_preview(self, obj):
    #     if obj.photo:
    #         return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
    #     return _("Pas de photo")
    # photo_preview.short_description = _("Photo")
