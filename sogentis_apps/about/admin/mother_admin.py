from django.contrib import admin
from parler.admin import TranslatableAdmin

from about.models import Mother


@admin.register(Mother)
class MotherAdmin(TranslatableAdmin):
    """
    Admin professionnel pour le modèle Mother.
    Compatible Parler (champs translatables).
    Optimisé pour ONG (listes, filtres, recherche...).
    """

    list_display = (
        "translated_name",
        "country",
        "marital_status",
        "number_of_children",
        "monthly_income",
        "currency",
        "capital_amount",        # ⭐ Nouveau
        "age",
    )

    list_filter = (
        "marital_status",
        "country",
        "currency",
    )

    search_fields = (
        "translations__name",
        "identification_number",
    )

    fieldsets = (
        (None, {
            "fields": ("photo", "birth_date", "country", "identification_number")
        }),
        ("Informations personnelles", {
            "fields": (
                "marital_status",
                "number_of_children",
            )
        }),
        ("Informations économiques", {
            "fields": (
                "monthly_income",
                "currency",
                "support_needed",
                "capital_amount",    # ⭐ Ajouté ici
            )
        }),
        ("Contenu multilingue", {
            "fields": (
                "name",
                "story",
                "activity",
            )
        }),
    )

    # Méthode utilitaire pour afficher le nom traduit
    def translated_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)

    translated_name.short_description = "Nom"

