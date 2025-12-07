# about/admin/organigram_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin

from about.models import Organigram
from about.forms import OrganigramForm


def _has_field(model, field_name: str) -> bool:
    return field_name in {f.name for f in model._meta.get_fields()}


@admin.register(Organigram)
class OrganigramAdmin(TranslatableAdmin):
    """
    Admin robuste pour Organigram :
    - N'ajoute dans list_display / list_filter que les champs existants.
    - Affiche un titre traduit si possible, sinon un fallback lisible.
    """
    form = OrganigramForm
    # Pas de list_display statique → on la construit dynamiquement.

    # ---------- list_display dynamique ----------
    def get_list_display(self, request):
        fields = []

        # Titre (priorité aux champs traduisibles 'title' / sinon 'name')
        if _has_field(Organigram, "title"):
            fields.append("title_translated")
        elif _has_field(Organigram, "name"):
            fields.append("name")

        # Miniature si un champ image existe
        if any(_has_field(Organigram, f) for f in ("photo", "image", "picture", "avatar", "icon")):
            fields.append("image_thumb")

        # Quelques champs fréquents si présents
        for candidate in ("position", "parent", "order", "country"):
            if _has_field(Organigram, candidate):
                fields.append(candidate)

        # Fallback minimal si rien trouvé
        if not fields:
            fields = ("__str__",)

        return tuple(fields)

    # ---------- list_filter dynamique ----------
    def get_list_filter(self, request):
        filters = []
        for candidate in ("position", "parent", "country", "order"):
            if _has_field(Organigram, candidate):
                filters.append(candidate)
        return tuple(filters)

    # ---------- search_fields dynamique ----------
    def get_search_fields(self, request):
        fields = []
        # Parler : champs de traduction courants
        for candidate in ("title", "name"):
            if _has_field(Organigram, candidate):
                # Si Parler est utilisé, les champs traduits se recherchent via translations__*
                fields.append(f"translations__{candidate}")
        # Champs non traduits fréquents
        for candidate in ("position", "country"):
            if _has_field(Organigram, candidate):
                fields.append(candidate)
        return tuple(fields)

    # ---------- helpers d’affichage ----------
    def title_translated(self, obj):
        """
        Si le modèle est translatable et possède 'title', l'afficher dans n'importe quelle langue,
        sinon fallback lisible.
        """
        getter = getattr(obj, "safe_translation_getter", None)
        if callable(getter) and _has_field(Organigram, "title"):
            return getter("title", any_language=True) or "-"
        # Fallback : name → str(obj)
        if _has_field(Organigram, "name"):
            return getattr(obj, "name", "-") or "-"
        return str(obj) if obj else "-"
    title_translated.short_description = "Titre"

    def image_thumb(self, obj):
        """
        Affiche une miniature si un champ image existe (photo, image, picture, avatar, icon).
        """
        for fname in ("photo", "image", "picture", "avatar", "icon"):
            if _has_field(Organigram, fname):
                f = getattr(obj, fname, None)
                if f and getattr(f, "url", None):
                    return format_html(
                        '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;" />',
                        f.url,
                    )
        return "-"
    image_thumb.short_description = "Aperçu"



# # about/admin/organigram_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from about.models.organigram import Organigram

# @admin.register(Organigram)
# class OrganigramAdmin(TranslatableAdmin):
#     list_display = ("title_translated",)

#     def title_translated(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     title_translated.short_description = "Titre"
