# about/admin/child_admin.py
from datetime import date
import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html

from parler.admin import TranslatableAdmin

from about.models.child import Child
from about.forms.forms import ChildForm  # ← adapte à ton import (ou: from about.forms import ChildForm)

# --------------------------------------------
# CONSTANTES
# --------------------------------------------
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_SUBDIR = "children"  # sous-dossier par défaut sous MEDIA_ROOT/


# --------------------------------------------
# SCAN SÉCURISÉ DES IMAGES SOUS MEDIA_ROOT
# --------------------------------------------
def _safe_media_scan(subdir: str = DEFAULT_SUBDIR):
    """
    Liste les images autorisées sous MEDIA_ROOT/subdir.
    Retourne une liste de dicts {rel, url, size_kb, name}.
    """
    media_root = Path(settings.MEDIA_ROOT).resolve()
    base = (media_root / subdir).resolve()

    images = []
    if not base.exists():
        return images

    for root, _, files in os.walk(base):
        for fname in files:
            fpath = Path(root) / fname

            # sécurité : ne jamais sortir de MEDIA_ROOT
            if not str(fpath.resolve()).startswith(str(media_root) + os.sep):
                continue

            mime, _ = mimetypes.guess_type(str(fpath))
            if mime not in ALLOWED_MIMES:
                continue

            rel = str(fpath.resolve().relative_to(media_root)).replace("\\", "/")
            url = settings.MEDIA_URL.rstrip("/") + "/" + rel
            size_kb = max(1, fpath.stat().st_size // 1024)

            images.append({
                "rel": rel,
                "url": url,
                "name": fname,
                "size_kb": size_kb,
            })

    images.sort(key=lambda x: x["name"].lower())
    return images


@admin.register(Child)
class ChildAdmin(TranslatableAdmin):
    """
    Admin pour le modèle Child.
    Affiche le nom, âge, école et classe.
    Compatible django-parler (nom traduit).
    """
    form = ChildForm

    list_display = [
        "photo_thumbnail",
        "display_name",
        "display_age",
        "display_school_name",
        "display_school_class",
        "identification_number",
        "country",
    ]
    search_fields = ["translations__name", "identification_number", "school_name"]
    list_filter = ["school_class", "country"]
    actions = ["attacher_photo_existante"]

    # -------------------------------------------------
    # Colonnes personnalisées
    # -------------------------------------------------
    @admin.display(description="Nom")
    def display_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"

    @admin.display(description="Âge")
    def display_age(self, obj):
        if not getattr(obj, "birth_date", None):
            return "-"
        today = date.today()
        bd = obj.birth_date
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

    @admin.display(description="École")
    def display_school_name(self, obj):
        return getattr(obj, "school_name", None) or "-"

    @admin.display(description="Classe")
    def display_school_class(self, obj):
        return getattr(obj, "school_class", None) or "-"

    @admin.display(description="Photo")
    def photo_thumbnail(self, obj):
        if getattr(obj, "photo", None):
            try:
                return format_html(
                    '<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;" />',
                    obj.photo.url
                )
            except Exception:
                pass
        return "-"

    # -------------------------------------------------
    # ACTION : Attacher une photo existante déjà sur le serveur
    # -------------------------------------------------
    def attacher_photo_existante(self, request, queryset):
        """
        GET  : affiche les images sous MEDIA_ROOT/children/
        POST : attache l'image sélectionnée (chemin relatif) au champ photo
        """
        # Appliquer (POST)
        if "apply" in request.POST:
            rel = request.POST.get("relative_path")
            if not rel:
                self.message_user(request, "Aucune image sélectionnée.", level=messages.WARNING)
                return redirect(request.get_full_path())

            count = 0
            for obj in queryset:
                obj.photo.name = rel  # chemin relatif sous MEDIA_ROOT
                obj.save(update_fields=["photo"])
                count += 1

            self.message_user(
                request,
                f"📸 Image « {rel} » attachée à {count} enfant(s).",
                level=messages.SUCCESS
            )
            return redirect(reverse("admin:about_child_changelist"))

        # Affichage (GET)
        subdir = (request.GET.get("subdir") or DEFAULT_SUBDIR).strip().strip("/\\") or DEFAULT_SUBDIR
        images = _safe_media_scan(subdir=subdir)

        context = {
            **self.admin_site.each_context(request),
            "title": "Choisir une photo existante",
            "images": images,
            "queryset": queryset,
            "subdir": subdir,
            "opts": self.model._meta,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, "admin/about/child_choose_image.html", context)

    attacher_photo_existante.short_description = "📷 Attacher une photo existante (MEDIA_ROOT/children/)"








# # about/admin/child_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from about.models.child import Child
# from datetime import date

# @admin.register(Child)
# class ChildAdmin(TranslatableAdmin):
#     """
#     Admin pour le modèle Child.
#     Affiche le nom, âge, école et classe dans la liste.
#     Compatible avec django-parler pour la traduction.
#     """
#     list_display = [
#         "display_name",
#         "display_age",
#         "display_school_name",
#         "display_school_class",
#         "identification_number",
#         "country",
#     ]
#     search_fields = ["translations__name", "identification_number", "school_name"]
#     list_filter = ["school_class", "country"]

#     # -------------------------------------------------
#     # Méthodes d'affichage personnalisées
#     # -------------------------------------------------
#     @admin.display(description="Nom")
#     def display_name(self, obj):
#         return obj.safe_translation_getter("name", any_language=True) or "-"

#     @admin.display(description="Âge")
#     def display_age(self, obj):
#         if not obj.birth_date:
#             return "-"
#         today = date.today()
#         age = today.year - obj.birth_date.year - (
#             (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
#         )
#         return age

#     @admin.display(description="École")
#     def display_school_name(self, obj):
#         return obj.school_name or "-"

#     @admin.display(description="Classe")
#     def display_school_class(self, obj):
#         return obj.school_class or "-"

#     # -------------------------------------------------
#     # Ajout d’une vue miniature de la photo dans l’admin
#     # -------------------------------------------------
#     @admin.display(description="Photo")
#     def photo_thumbnail(self, obj):
#         if obj.photo:
#             return f'<img src="{obj.photo.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />'
#         return "-"
#     photo_thumbnail.allow_tags = True

#     # Optionnel : ajouter photo dans list_display si besoin
#     # list_display.append("photo_thumbnail")


