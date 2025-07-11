# # social/models/evenement.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Evenement(models.Model):
    titre = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    date = models.DateTimeField(_("Date de l'événement"))
    lieu = models.CharField(_("Lieu"), max_length=255)
    is_public = models.BooleanField(_("Visible publiquement ?"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Événement")
        verbose_name_plural = _("Événements")
        ordering = ['-date']

    def __str__(self):
        return f"{self.titre} - {self.date.strftime('%d/%m/%Y %H:%M')}"
