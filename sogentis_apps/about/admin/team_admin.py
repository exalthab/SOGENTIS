# about/admin/team_admin.py

from django.contrib import admin
from parler.admin import TranslatableAdmin
from about.models.team_member import TeamMember
from django.utils.html import format_html


@admin.register(TeamMember)
class TeamMemberAdmin(TranslatableAdmin):
    list_display = ["photo_preview", "name_translated", "role_label", "category", "order"]
    list_editable = ["order"]
    search_fields = ["translations__name", "translations__role"]
    list_filter = ["category"]
    readonly_fields = ["photo_preview"]

    fieldsets = (
        (None, {"fields": ("name", "role", "category", "order")}),
        ("Photo", {"fields": ("photo", "photo_preview")}),
        ("Biographie", {"fields": ("bio",)}),
    )

    # -------------------------------------------------
    # Affiche le nom traduit
    # -------------------------------------------------
    def name_translated(self, obj):
        return obj.safe_translation_getter("name", any_language=True)
    name_translated.short_description = "Nom"

    # -------------------------------------------------
    # Affiche le rôle selon la catégorie
    # -------------------------------------------------
    def role_label(self, obj):
        role = obj.safe_translation_getter("role", any_language=True)
        if obj.category == "board":
            return "Conseil d'administration"
        elif obj.category == "employee":
            return role or "Employé"
        return role
    role_label.short_description = "Rôle"

    # -------------------------------------------------
    # Aperçu photo ronde dans la liste
    # -------------------------------------------------
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; object-fit:cover; border-radius:50%;"/>',
                obj.photo.url,
            )
        return "Pas de photo"
    photo_preview.short_description = "Photo"



