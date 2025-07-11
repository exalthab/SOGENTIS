# social/models/engagement.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Engagement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur")
    )
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"))
    date = models.DateField(_("Date de l’engagement"))
    is_active = models.BooleanField(_("Actif ?"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Engagement")
        verbose_name_plural = _("Engagements")
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"
