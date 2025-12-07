# about/forms/forms.py
from __future__ import annotations
from typing import Iterable, Optional, Tuple

import mimetypes
import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from parler.forms import TranslatableModelForm

# Modèles (ajuste le chemin si besoin)
from about.models import (
    TeamMember, HeroBlock, Child, Mother, Partner, Organigram, AboutSubsection
)

# Essaie d'utiliser le widget CKEditor5 ; fallback Textarea sinon
try:
    from django_ckeditor_5.widgets import CKEditor5Widget

    def ckeditor_widget():
        return CKEditor5Widget(config_name="default")
except Exception:
    def ckeditor_widget():
        return forms.Textarea(attrs={"class": "ckeditor5"})


# =====================================================================================
# Réglages par défaut (surchargables via settings.py)
# =====================================================================================
ABOUT_MAX_IMAGE_MB: int = getattr(settings, "ABOUT_MAX_IMAGE_MB", 25)  # Mo
ABOUT_ALLOWED_IMAGE_MIME_TYPES: Iterable[str] = getattr(
    settings,
    "ABOUT_ALLOWED_IMAGE_MIME_TYPES",
    ("image/jpeg", "image/png", "image/webp"),
)

# (None = pas de contrainte). Tu peux définir ces variables dans settings si besoin.
ABOUT_MIN_IMAGE_SIZE: Optional[Tuple[int, int]] = getattr(
    settings, "ABOUT_MIN_IMAGE_SIZE", None
)  # (w, h)
ABOUT_MAX_IMAGE_SIZE: Optional[Tuple[int, int]] = getattr(
    settings, "ABOUT_MAX_IMAGE_SIZE", None
)  # (w, h)

# Par modèle (facultatif) — exemple : forcer bannières larges pour le Hero
HERO_MIN_SIZE: Optional[Tuple[int, int]] = getattr(settings, "HERO_MIN_SIZE", (1200, 600))
HERO_MAX_SIZE: Optional[Tuple[int, int]] = getattr(settings, "HERO_MAX_SIZE", None)


# =====================================================================================
# Mixin générique de validation d'image
# =====================================================================================
class ImageValidationMixin:
    """
    À utiliser dans les ModelForm qui ont des ImageField :
        - self.clean_image_field("photo")
        - self.clean_image_field("background_image", min_size=(1200, 600))

    Les limites par défaut viennent des constantes ABOUT_*, mais tu peux
    les surcharger par champ via les paramètres.
    """

    def clean_image_field(
        self,
        field_name: str,
        *,
        max_mb: Optional[int] = None,
        allowed_mimes: Optional[Iterable[str]] = None,
        min_size: Optional[Tuple[int, int]] = None,
        max_size: Optional[Tuple[int, int]] = None,
    ) -> None:
        f = self.cleaned_data.get(field_name)
        if not f:
            return

        # Taille
        max_bytes = (max_mb or ABOUT_MAX_IMAGE_MB) * 1024 * 1024
        if getattr(f, "size", 0) and f.size > max_bytes:
            raise ValidationError(
                f"Le fichier ne doit pas dépasser {(max_mb or ABOUT_MAX_IMAGE_MB)} Mo."
            )

        # Type MIME
        content_type = getattr(f, "content_type", None)
        if not content_type:
            guessed, _ = mimetypes.guess_type(getattr(f, "name", ""))
            content_type = guessed

        allowed = tuple(allowed_mimes or ABOUT_ALLOWED_IMAGE_MIME_TYPES)
        if content_type not in allowed:
            allowed_str = ", ".join(allowed)
            raise ValidationError(f"Formats autorisés : {allowed_str}.")

        # Dimensions
        try:
            width, height = get_image_dimensions(f)
        except Exception:
            raise ValidationError("Fichier image invalide ou corrompu.")

        eff_min = min_size or ABOUT_MIN_IMAGE_SIZE
        if eff_min:
            min_w, min_h = eff_min
            if (min_w and width < min_w) or (min_h and height < min_h):
                raise ValidationError(f"Dimensions trop petites (min {min_w}×{min_h}px).")

        eff_max = max_size or ABOUT_MAX_IMAGE_SIZE
        if eff_max:
            max_w, max_h = eff_max
            if (max_w and width > max_w) or (max_h and height > max_h):
                raise ValidationError(f"Dimensions trop grandes (max {max_w}×{max_h}px).")


# =====================================================================================
# FORMS
# =====================================================================================

# ------------------------
# TEAM MEMBER
# ------------------------
class TeamMemberForm(ImageValidationMixin, TranslatableModelForm):
    class Meta:
        model = TeamMember
        fields = ["name", "role", "category", "order", "photo", "bio"]
        widgets = {
            "bio": ckeditor_widget(),
        }

    def clean(self):
        cleaned = super().clean()
        self.clean_image_field("photo")
        return cleaned


# ------------------------
# HERO (bannière)
# ------------------------
class HeroForm(ImageValidationMixin, TranslatableModelForm):
    class Meta:
        model = HeroBlock
        fields = ["title", "subtitle", "background_image", "button_text", "button_link"]

    def clean(self):
        cleaned = super().clean()
        # Pour un hero, impose des dimensions plus larges par défaut
        self.clean_image_field(
            "background_image",
            min_size=HERO_MIN_SIZE,
            max_size=HERO_MAX_SIZE,
        )
        return cleaned


# ------------------------
# CHILD  (corrigé : 'description' au lieu de 'story')
# ------------------------
class ChildForm(ImageValidationMixin, TranslatableModelForm):
    class Meta:
        model = Child
        # Ne liste que des champs sûrs (présents dans ton modèle) pour éviter FieldError
        fields = ["name", "description", "photo"]
        widgets = {
            "description": ckeditor_widget(),
        }

    def clean(self):
        cleaned = super().clean()
        self.clean_image_field("photo")
        return cleaned


# ------------------------
# MOTHER
# ------------------------
class MotherForm(ImageValidationMixin, TranslatableModelForm):
    class Meta:
        model = Mother
        fields = ["name", "photo", "story"]
        widgets = {
            "story": ckeditor_widget(),
        }

    def clean(self):
        cleaned = super().clean()
        self.clean_image_field("photo")
        return cleaned


# ------------------------
# PARTNER
# ------------------------
class PartnerForm(ImageValidationMixin, TranslatableModelForm):
    class Meta:
        model = Partner
        fields = ["name", "logo", "website"]

    def clean(self):
        cleaned = super().clean()
        self.clean_image_field("logo")
        return cleaned


# ------------------------
# ORGANIGRAM (translatable et robuste)
# ------------------------
from django.forms import ModelForm

class OrganigramForm(ImageValidationMixin, TranslatableModelForm):
    class Meta:
        model = Organigram
        # On prend tous les champs existants pour éviter les FieldError
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si le modèle a un champ riche, on lui met CKEditor5
        for candidate in ("content", "description", "body", "notes"):
            if candidate in self.fields:
                self.fields[candidate].widget = ckeditor_widget()

        # (optionnel) petites aides d'UI si ces champs existent
        if "title" in self.fields:
            self.fields["title"].help_text = self.fields["title"].help_text or "Titre de l’élément de l’organigramme"
        if "parent" in self.fields:
            self.fields["parent"].help_text = self.fields["parent"].help_text or "Parent/superviseur dans l’organigramme"

    def clean(self):
        cleaned = super().clean()
        # Valide l’image uniquement si le champ existe vraiment
        for img_field in ("photo", "image", "picture", "avatar", "icon"):
            if img_field in self.fields and img_field in self.cleaned_data:
                self.clean_image_field(img_field)
                break
        return cleaned


# ------------------------
# ABOUT SUBSECTION (Parler)
# ------------------------
class AboutSubsectionForm(TranslatableModelForm):
    class Meta:
        model = AboutSubsection
        fields = ["title", "subtitle", "content"]
        widgets = {
            "content": ckeditor_widget(),
        }


# =====================================================================================
# (Optionnel) Form utilitaire : lier une image déjà sur le serveur (MEDIA_ROOT)
# =====================================================================================
class AttachExistingMediaForm(forms.Form):
    """
    Permet d'associer un fichier déjà présent sous MEDIA_ROOT à un champ ImageField :
        form = AttachExistingMediaForm(request.POST)
        if form.is_valid():
            rel = form.cleaned_data["relative_path"]  # ex: "team/jane.jpg"
            obj.photo.name = rel
            obj.save()
    """
    relative_path = forms.CharField(
        label="Chemin relatif depuis MEDIA_ROOT (ex: team/jane.jpg)",
        help_text="Le fichier doit déjà exister physiquement sous MEDIA_ROOT.",
        max_length=500,
    )

    def clean_relative_path(self):
        rel = (self.cleaned_data.get("relative_path") or "").lstrip("/").strip()
        if not rel:
            raise ValidationError("Chemin relatif requis (ex: team/jane.jpg).")

        media_root = getattr(settings, "MEDIA_ROOT", "")
        if not media_root:
            raise ValidationError("MEDIA_ROOT n'est pas configuré.")

        abs_path = os.path.abspath(os.path.join(media_root, rel))
        # sécurité: ne jamais sortir de MEDIA_ROOT
        if not abs_path.startswith(os.path.abspath(media_root) + os.sep):
            raise ValidationError("Chemin en dehors de MEDIA_ROOT interdit.")
        if not os.path.exists(abs_path):
            raise ValidationError("Le fichier n'existe pas sous MEDIA_ROOT.")

        mime, _ = mimetypes.guess_type(abs_path)
        if mime not in ABOUT_ALLOWED_IMAGE_MIME_TYPES:
            allowed_str = ", ".join(ABOUT_ALLOWED_IMAGE_MIME_TYPES)
            raise ValidationError(f"Format non autorisé. Formats autorisés : {allowed_str}.")

        return rel
