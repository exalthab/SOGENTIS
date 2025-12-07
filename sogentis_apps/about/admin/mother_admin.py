# about/admin/mother_admin.py
from __future__ import annotations

import mimetypes
import os
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html
from parler.admin import TranslatableAdmin

from about.models import Mother
from about.forms.forms import MotherForm  # ← adapte si tu ré-exportes: from about.forms import MotherForm

# --------------------------------------------
# CONSTANTES
# --------------------------------------------
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_SUBDIR = "mothers"  # sous-dossier par défaut sous MEDIA_ROOT/


# --------------------------------------------
# SCAN SÉCURISÉ DES IMAGES SOUS MEDIA_ROOT
# --------------------------------------------
def _safe_media_scan(subdir: str = DEFAULT_SUBDIR):
    """
    Liste les images autorisées sous MEDIA_ROOT/subdir.
    Retourne [{rel, url, name, size_kb}, ...].
    """
    media_root = Path(settings.MEDIA_ROOT).resolve()
    base = (media_root / subdir).resolve()
    images = []

    if not base.exists():
        return images

    for root, _, files in os.walk(base):
        for fname in files:
            fpath = Path(root) / fname

            # sécurité : rester sous MEDIA_ROOT
            if not str(fpath.resolve()).startswith(str(media_root) + os.sep):
                continue

            mime, _ = mimetypes.guess_type(str(fpath))
            if mime not in ALLOWED_MIMES:
                continue

            rel = str(fpath.resolve().relative_to(media_root)).replace("\\", "/")
            url = settings.MEDIA_URL.rstrip("/") + "/" + rel
            size_kb = max(1, fpath.stat().st_size // 1024)

            images.append({"rel": rel, "url": url, "name": fname, "size_kb": size_kb})

    images.sort(key=lambda x: x["name"].lower())
    return images


@admin.register(Mother)
class MotherAdmin(TranslatableAdmin):
    """
    Admin professionnel pour le modèle Mother.
    Compatible Parler (champs translatables).
    Optimisé pour ONG (listes, filtres, recherche...).
    """
    form = MotherForm

    list_display = (
        "photo_thumbnail",
        "translated_name",
        "country",
        "marital_status",
        "number_of_children",
        "monthly_income",
        "currency",
        "capital_amount",
        "age",
    )
    list_filter = ("marital_status", "country", "currency")
    search_fields = ("translations__name", "identification_number")
    actions = ["attacher_photo_existante"]

    fieldsets = (
        (None, {
            "fields": ("photo", "birth_date", "country", "identification_number")
        }),
        ("Informations personnelles", {
            "fields": ("marital_status", "number_of_children")
        }),
        ("Informations économiques", {
            "fields": ("monthly_income", "currency", "support_needed", "capital_amount")
        }),
        ("Contenu multilingue", {
            "fields": ("name", "story", "activity")
        }),
    )

    # ---------- Helpers affichage ----------
    @admin.display(description="Nom")
    def translated_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"

    @admin.display(description="Âge")
    def age(self, obj):
        bd = getattr(obj, "birth_date", None)
        if not bd:
            return "-"
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

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

    # ---------- Action : attacher une photo existante ----------
    def attacher_photo_existante(self, request, queryset):
        """
        GET  : affiche les images sous MEDIA_ROOT/mothers/
        POST : attache l'image choisie au champ photo
        """
        # POST → appliquer
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
                f"📷 Image « {rel} » attachée à {count} mère(s).",
                level=messages.SUCCESS
            )
            return redirect(reverse("admin:about_mother_changelist"))

        # GET → écran de choix
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
        # On fera le template après (même pattern que team/child)
        return render(request, "admin/about/mother_choose_image.html", context)

    attacher_photo_existante.short_description = "📷 Attacher une photo existante (MEDIA_ROOT/mothers/)"






# # about/admin/mother_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from about.models import Mother


# @admin.register(Mother)
# class MotherAdmin(TranslatableAdmin):
#     """
#     Admin professionnel pour le modèle Mother.
#     Compatible Parler (champs translatables).
#     Optimisé pour ONG (listes, filtres, recherche...).
#     """

#     list_display = (
#         "translated_name",
#         "country",
#         "marital_status",
#         "number_of_children",
#         "monthly_income",
#         "currency",
#         "capital_amount",        # ⭐ Nouveau
#         "age",
#     )

#     list_filter = (
#         "marital_status",
#         "country",
#         "currency",
#     )

#     search_fields = (
#         "translations__name",
#         "identification_number",
#     )

#     fieldsets = (
#         (None, {
#             "fields": ("photo", "birth_date", "country", "identification_number")
#         }),
#         ("Informations personnelles", {
#             "fields": (
#                 "marital_status",
#                 "number_of_children",
#             )
#         }),
#         ("Informations économiques", {
#             "fields": (
#                 "monthly_income",
#                 "currency",
#                 "support_needed",
#                 "capital_amount",    # ⭐ Ajouté ici
#             )
#         }),
#         ("Contenu multilingue", {
#             "fields": (
#                 "name",
#                 "story",
#                 "activity",
#             )
#         }),
#     )

#     # Méthode utilitaire pour afficher le nom traduit
#     def translated_name(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)

#     translated_name.short_description = "Nom"

