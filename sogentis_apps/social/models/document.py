# social/models/document.py
from __future__ import annotations

import os

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def document_upload_to(instance: "Document", filename: str) -> str:
    """
    Chemin d’upload : documents/YYYY/MM/<filename>
    (Simple, stable, pratique pour classer.)
    """
    return os.path.join("documents", instance.created_at.strftime("%Y/%m"), filename)


class Document(models.Model):
    """
    Document simple (PDF, DOCX, etc.)
    - Compatible avec ton module search/signals.py (title, description, file, author)
    - Peut être public ou privé (is_public)
    """

    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    file = models.FileField(
        _("Fichier"),
        upload_to=document_upload_to,
        blank=False,
        null=False,
        help_text=_("PDF, DOCX, image, etc."),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="social_documents",
        verbose_name=_("Auteur"),
    )

    is_public = models.BooleanField(_("Visible publiquement ?"), default=True)

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title or f"Document #{self.pk}"

    @property
    def file_url(self) -> str:
        """URL du fichier si accessible."""
        try:
            return self.file.url if self.file else ""
        except Exception:
            return ""

    @property
    def filename(self) -> str:
        """Nom de fichier (basename)."""
        try:
            return os.path.basename(self.file.name) if self.file else ""
        except Exception:
            return ""

    def get_absolute_url(self) -> str:
        """
        URL de détail (à adapter à tes urls.py si tu as une route dédiée).
        Si tu n’as pas encore de page document, tu peux laisser '#'.
        """
        try:
            return reverse("social:document_detail", kwargs={"pk": self.pk})
        except Exception:
            return "#"






# # social/models/document.py

# from django.db import models

# class Document(models.Model):
#     title = models.CharField(max_length=255)
#     file = models.FileField(upload_to='documents/')
#     # ... other fields

