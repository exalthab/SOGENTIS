# about/admin/child_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin
from about.models.child import Child
from datetime import date

@admin.register(Child)
class ChildAdmin(TranslatableAdmin):
    """
    Admin pour le modèle Child.
    Affiche le nom, âge, école et classe dans la liste.
    Compatible avec django-parler pour la traduction.
    """
    list_display = [
        "display_name",
        "display_age",
        "display_school_name",
        "display_school_class",
        "identification_number",
        "country",
    ]
    search_fields = ["translations__name", "identification_number", "school_name"]
    list_filter = ["school_class", "country"]

    # -------------------------------------------------
    # Méthodes d'affichage personnalisées
    # -------------------------------------------------
    @admin.display(description="Nom")
    def display_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"

    @admin.display(description="Âge")
    def display_age(self, obj):
        if not obj.birth_date:
            return "-"
        today = date.today()
        age = today.year - obj.birth_date.year - (
            (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
        )
        return age

    @admin.display(description="École")
    def display_school_name(self, obj):
        return obj.school_name or "-"

    @admin.display(description="Classe")
    def display_school_class(self, obj):
        return obj.school_class or "-"

    # -------------------------------------------------
    # Ajout d’une vue miniature de la photo dans l’admin
    # -------------------------------------------------
    @admin.display(description="Photo")
    def photo_thumbnail(self, obj):
        if obj.photo:
            return f'<img src="{obj.photo.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />'
        return "-"
    photo_thumbnail.allow_tags = True

    # Optionnel : ajouter photo dans list_display si besoin
    # list_display.append("photo_thumbnail")


