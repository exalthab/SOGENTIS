# accounts_users/models/users_settings.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_("Utilisateur")
    )

    receive_newsletter = models.BooleanField(
        _("Recevoir la newsletter"),
        default=True
    )
    dark_mode = models.BooleanField(
        _("Mode sombre activé"),
        default=False
    )
    language = models.CharField(
        _("Langue préférée"),
        max_length=10,
        choices=[
            ('fr', _("Français")),
            ('en', _("Anglais")),
        ],
        default='fr'
    )

    created_at = models.DateTimeField(
        _("Créé le"),
        default=timezone.now,
        editable=False
    )
    updated_at = models.DateTimeField(
        _("Mis à jour le"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Paramètre utilisateur")
        verbose_name_plural = _("Paramètres utilisateurs")
        ordering = ['-created_at']

    def __str__(self):
        return f"Paramètres de {self.user.email}"





## accounts_users/models/users_settings.py -> 01/07
# from django.db import models
# from django.conf import settings

# class UserSettings(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     language = models.CharField(max_length=10, default='fr')
#     notifications_enabled = models.BooleanField(default=True)

#     def __str__(self):
#         return f"Settings for {self.user.email}"
