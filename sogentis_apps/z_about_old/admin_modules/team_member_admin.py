#about/admin_modules/team_member_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from z_about_old.models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(TranslatableAdmin):
    """
    Administration des membres de l'équipe.
    """
    list_display = ("get_name", "get_role", "order", "photo_preview", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("translations__name", "translations__role")
    ordering = ("order",)
    readonly_fields = ("photo_preview", "created_at", "updated_at")

    fieldsets = (
        (_("Informations personnelles"), {
            "fields": ("about_page", "name", "role", "bio", "photo", "photo_preview"),
        }),
        (_("Contacts"), {
            "fields": ("email", "linkedin", "twitter"),
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

    def get_role(self, obj):
        return obj.safe_translation_getter("role", any_language=True)
    get_role.short_description = _("Rôle")

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:50%;">',
                obj.photo.url
            )
        return "—"
    photo_preview.short_description = _("Aperçu photo")





# #about/admin_modules/team_member_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.team_member import TeamMember


# @admin.register(TeamMember)
# class TeamMemberAdmin(TranslatableAdmin):
#     list_display = ("name", "role", "order", "photo_preview")
#     search_fields = ("translations__name", "translations__role")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("order", "is_active")

#     fieldsets = (
#         ("Informations personnelles", {"fields": ("name", "role", "bio", "photo", "photo_preview", "email", "linkedin", "twitter", "is_active")}),
#         ("Ordre & Dates", {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>',
#                 obj.photo.url
#             )
#         return "Pas de photo"
#     photo_preview.short_description = "Photo"