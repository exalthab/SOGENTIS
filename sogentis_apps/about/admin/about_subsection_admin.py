# about/admin/about_subsection_admin.py
from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html
from parler.admin import TranslatableAdmin

from about.models import AboutSubsection

# -------------------------------------------------------------------
# Config / constantes
# -------------------------------------------------------------------
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}
# Dossier conseillé pour stocker les images des sous-sections
DEFAULT_SUBDIR = "about/subsections"   # => MEDIA_ROOT/about/subsections/*


def _safe_media_scan(subdir: str = DEFAULT_SUBDIR):
    """
    Liste sécurisée des images autorisées sous MEDIA_ROOT/subdir.
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

@admin.register(AboutSubsection)
class AboutSubsectionAdmin(TranslatableAdmin):
    """
    Admin pro pour AboutSubsection (Parler).
    Affiche état/ordre + titre traduit, vignette, action “attacher image existante”.
    """

    # --- Listing ---
    list_display = ("thumb", "title_translated", "key", "slug", "is_active", "order")
    list_editable = ("is_active", "order")
    search_fields = ("translations__title", "key", "slug")
    ordering = ("order",)
    readonly_fields = ("thumb",)

    # --- Actions ---
    actions = ["attacher_image_existante"]

    # --- Fieldsets (les champs traduits utilisent les noms simples Parler) ---
    fieldsets = (
        (None, {
            "fields": ("key", "slug", "is_active", "order")
        }),
        ("Contenu multilingue", {
            "fields": ("title", "subtitle", "content", "image", "thumb"),
            "description": "Les champs ci-dessous sont traduits (Parler)."
        }),
    )

    # -------------------------------------------------------------------
    # Helpers affichage
    # -------------------------------------------------------------------
    @admin.display(description="Titre")
    def title_translated(self, obj):
        # si 'title' est bien un champ translatable
        return obj.safe_translation_getter("title", any_language=True) or "-"

    @admin.display(description="Aperçu")
    def thumb(self, obj):
        # si 'image' est un champ translatable, l’attribut est directement accessible
        img = getattr(obj, "image", None)
        if img:
            try:
                return format_html(
                    '<img src="{}" style="width:72px; height:48px; object-fit:cover; border-radius:6px;"/>',
                    img.url
                )
            except Exception:
                pass
        return "-"

    # -------------------------------------------------------------------
    # Action : attacher une image existante (MEDIA_ROOT/about/subsections/)
    # -------------------------------------------------------------------
    def attacher_image_existante(self, request, queryset):
        """
        GET  : affiche les fichiers sous MEDIA_ROOT/about/subsections/
        POST : attache le fichier choisi au champ 'image' (traduit)
        """
        # POST → appliquer
        if "apply" in request.POST:
            rel = request.POST.get("relative_path")
            if not rel:
                self.message_user(request, "Aucune image sélectionnée.", level=messages.WARNING)
                return redirect(request.get_full_path())

            count = 0
            for obj in queryset:
                # Pour un champ translatable (Parler), l’assignation se fait pareil :
                # obj.image.name = rel
                # Si tu utilises des variantes par langue, l’admin de Parler est déjà en langue courante.
                obj.image.name = rel
                obj.save(update_fields=["image"])
                count += 1

            self.message_user(
                request,
                f"🖼️ Image « {rel} » attachée à {count} sous-section(s).",
                level=messages.SUCCESS
            )
            return redirect(reverse("admin:about_aboutsubsection_changelist"))

        # GET → affichage de la grille
        subdir = (request.GET.get("subdir") or DEFAULT_SUBDIR).strip().strip("/\\") or DEFAULT_SUBDIR
        images = _safe_media_scan(subdir=subdir)

        context = {
            **self.admin_site.each_context(request),
            "title": "Choisir une image existante",
            "images": images,
            "queryset": queryset,
            "subdir": subdir,
            "opts": self.model._meta,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        # Template à créer (même pattern que team/child/mother/hero/partner/organigram)
        return render(request, "admin/about/aboutsubsection_choose_image.html", context)

    attacher_image_existante.short_description = "🖼️ Attacher une image existante (MEDIA_ROOT/about/subsections/)"







# # about/admin/about_subsection_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from about.models import AboutSubsection

# @admin.register(AboutSubsection)
# class AboutSubsectionAdmin(TranslatableAdmin):
#     list_display = ("key", "slug", "is_active", "order")
#     list_editable = ("is_active", "order")
#     search_fields = ("translations__title",)
#     ordering = ("order",)

