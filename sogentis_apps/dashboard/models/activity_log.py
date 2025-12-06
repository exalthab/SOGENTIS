# dashboard/models/activity_log.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        verbose_name=_("Utilisateur")
    )
    action = models.CharField(_("Action"), max_length=255)
    timestamp = models.DateTimeField(_("Horodatage"), auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Activité utilisateur")
        verbose_name_plural = _("Activités utilisateur")

    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
