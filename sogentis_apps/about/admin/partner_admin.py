# about/admin/partner_admin.py
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

from about.models.partner import Partner
from about.forms.forms import PartnerForm  # si tu ré-exportes: from about.forms import PartnerForm

# --------------------------------------------
# Config / constantes
# --------------------------------------------
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp", "image/svg+xml"}
DEFAULT_SUBDIR = "partners"  # sous MEDIA_ROOT/partners/*


def _safe_media_scan(subdir: str = DEFAULT_SUBDIR):
    """
    Liste sécurisée des images sous MEDIA_ROOT/subdir.
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


@admin.register(Partner)
class PartnerAdmin(TranslatableAdmin):
    """
    Admin Partenaire (nom traduit, logo, site web).
    - Form PartnerForm (validation image)
    - Vignette logo
    - Action : attacher un logo existant (MEDIA_ROOT/partners/)
    """
    form = PartnerForm

    list_display = ["logo_thumb", "name_translated", "website"]
    search_fields = ["translations__name", "website"]
    readonly_fields = ["logo_thumb"]
    actions = ["attacher_logo_existant"]

    fieldsets = (
        (None, {
            "fields": ("name", "website")
        }),
        ("Logo", {
            "fields": ("logo", "logo_thumb"),
            "description": "Dépose un logo (PNG/JPG/WebP/SVG) ou utilise l’action pour choisir un fichier déjà sur le serveur."
        }),
    )

    # --------- Affichages ----------
    def name_translated(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"
    name_translated.short_description = "Nom"

    @admin.display(description="Logo")
    def logo_thumb(self, obj):
        if getattr(obj, "logo", None):
            try:
                return format_html(
                    '<img src="{}" alt="logo" style="height:40px; object-fit:contain; background:#fff; padding:4px; border:1px solid #eee; border-radius:6px;">',
                    obj.logo.url
                )
            except Exception:
                pass
        return "-"

    # --------- Action : attacher un logo existant ----------
    def attacher_logo_existant(self, request, queryset):
        """
        GET  : affiche les fichiers sous MEDIA_ROOT/partners/
        POST : attache le fichier sélectionné au champ 'logo'
        """
        # POST → appliquer
        if "apply" in request.POST:
            rel = request.POST.get("relative_path")
            if not rel:
                self.message_user(request, "Aucun fichier sélectionné.", level=messages.WARNING)
                return redirect(request.get_full_path())

            count = 0
            for obj in queryset:
                obj.logo.name = rel  # chemin relatif sous MEDIA_ROOT
                obj.save(update_fields=["logo"])
                count += 1

            self.message_user(
                request,
                f"🔗 Logo « {rel} » attaché à {count} partenaire(s).",
                level=messages.SUCCESS
            )
            return redirect(reverse("admin:about_partner_changelist"))

        # GET → affichage de la grille
        subdir = (request.GET.get("subdir") or DEFAULT_SUBDIR).strip().strip("/\\") or DEFAULT_SUBDIR
        images = _safe_media_scan(subdir=subdir)

        context = {
            **self.admin_site.each_context(request),
            "title": "Choisir un logo existant",
            "images": images,
            "queryset": queryset,
            "subdir": subdir,
            "opts": self.model._meta,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        # Template à créer ensuite (même pattern que team/child/mother/hero)
        return render(request, "admin/about/partner_choose_image.html", context)

    attacher_logo_existant.short_description = "🔗 Attacher un logo existant (MEDIA_ROOT/partners/)"





# #  about/admin/partner_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from about.models.partner import Partner

# @admin.register(Partner)
# class PartnerAdmin(TranslatableAdmin):
#     list_display = ['name', 'website']
#     search_fields = ['translations__name']

#     def name_translated(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)