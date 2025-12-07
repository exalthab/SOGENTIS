# about/admin/hero_admin.py
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

# Modèles / Forms
from about.models import HeroBlock
from about.forms.forms import HeroForm   # si tu ré-exportes: from about.forms import HeroForm

# ------------------------------------------------------------
# Constantes / Config
# ------------------------------------------------------------
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_SUBDIR = "hero"  # dossier par défaut sous MEDIA_ROOT/ (ex: /media/hero/*)


# ------------------------------------------------------------
# Scan sécurisé des médias sous MEDIA_ROOT/subdir
# ------------------------------------------------------------
def _safe_media_scan(subdir: str = DEFAULT_SUBDIR):
    """
    Retourne une liste d'images autorisées sous MEDIA_ROOT/subdir :
    [{rel, url, name, size_kb}, ...]
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

            rel = str(fpath.resolve()).replace(str(media_root) + os.sep, "").replace("\\", "/")
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


@admin.register(HeroBlock)
class HeroBlockAdmin(TranslatableAdmin):
    """
    Admin HeroBlock (bannière héro).
    - Form HeroForm (validation image + CKEditor5 si dispo)
    - Action : attacher une image déjà présente sous MEDIA_ROOT/hero/
    """
    form = HeroForm

    list_display = ("title_translated", "background_preview")
    readonly_fields = ("background_preview",)

    fieldsets = (
        (None, {
            "fields": ("title", "subtitle")
        }),
        ("Arrière-plan", {
            "fields": ("background_image", "background_preview"),
            "description": "Image large recommandée (ex: ≥ 1200×600 px)."
        }),
        ("Bouton (CTA)", {
            "fields": ("button_text", "button_link")  # ✅ correspond au modèle
        }),
    )

    actions = ["attacher_background_existant"]

    # ---------- list_display helpers ----------
    def title_translated(self, obj):
        return obj.safe_translation_getter("title", any_language=True) or "-"
    title_translated.short_description = "Titre"

    def background_preview(self, obj):
        if getattr(obj, "background_image", None):
            try:
                return format_html(
                    '<img src="{}" style="max-width:320px; max-height:160px; '
                    'object-fit:cover; border-radius:6px;" />',
                    obj.background_image.url
                )
            except Exception:
                pass
        return "-"
    background_preview.short_description = "Aperçu"

    # ---------- Action : attacher une image existante ----------
    def attacher_background_existant(self, request, queryset):
        """
        GET  : affiche la liste des images sous MEDIA_ROOT/hero/
        POST : attache l'image choisie à background_image
        """
        # POST → appliquer
        if "apply" in request.POST:
            rel = request.POST.get("relative_path")
            if not rel:
                self.message_user(request, "Aucune image sélectionnée.", level=messages.WARNING)
                return redirect(request.get_full_path())

            count = 0
            for obj in queryset:
                obj.background_image.name = rel  # chemin relatif sous MEDIA_ROOT
                obj.save(update_fields=["background_image"])
                count += 1

            self.message_user(
                request,
                f"🖼️ Image « {rel} » attachée à {count} HeroBlock(s).",
                level=messages.SUCCESS
            )
            return redirect(reverse("admin:about_heroblock_changelist"))

        # GET → affichage
        subdir = (request.GET.get("subdir") or DEFAULT_SUBDIR).strip().strip("/\\") or DEFAULT_SUBDIR
        images = _safe_media_scan(subdir=subdir)

        context = {
            **self.admin_site.each_context(request),
            "title": "Choisir une image d’arrière-plan existante",
            "images": images,
            "queryset": queryset,
            "subdir": subdir,
            "opts": self.model._meta,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        # Template à créer ensuite (comme pour team/child/etc.)
        return render(request, "admin/about/hero_choose_image.html", context)

    attacher_background_existant.short_description = "🖼️ Attacher une image existante (MEDIA_ROOT/hero/)"




# #admin hero_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from about.models import HeroBlock

# @admin.register(HeroBlock)
# class HeroBlockAdmin(TranslatableAdmin):
#     list_display = ("title_translated",)

#     def title_translated(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
