# social/models/publication.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Publication(models.Model):
    """
    Modèle pour une publication/news/article affiché sur le site,
    avec possibilité d'attacher un document PDF à télécharger.
    """
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    file = models.FileField(
        _("Document à télécharger (PDF)"),
        upload_to="publications/",
        blank=True,
        null=True,
        help_text=_("PDF ou document lié à cette publication (optionnel)")
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Auteur")
    )
    is_public = models.BooleanField(_("Visible publiquement ?"), default=True)

    class Meta:
        verbose_name = _("Publication")
        verbose_name_plural = _("Publications")
        ordering = ['-created_at']

    def __str__(self):
        return self.title



# class Publication(models.Model):
#     title = models.CharField(_("Titre"), max_length=255)
#     description = models.TextField(_("Description"), blank=True)  # Ajouté pour affichage
#     file = models.FileField(_("Document PDF"), upload_to="publications/")  # Ajouté pour stockage du fichier
#     is_public = models.BooleanField(_("Visible publiquement ?"), default=False)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

#     def __str__(self):
#         return self.title