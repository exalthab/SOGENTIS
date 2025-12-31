# accounts_users/models/users_settings.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel


class UserSettings(TimeStampedModel):
    """
    Paramètres utilisateur.
    Langue normalisée automatiquement (robuste, sans erreur bloquante).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name=_("Utilisateur"),
    )

    receive_newsletter = models.BooleanField(_("Recevoir la newsletter"), default=True)
    dark_mode = models.BooleanField(_("Mode sombre activé"), default=False)

    language = models.CharField(
        _("Langue préférée"),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )

    class Meta:
        verbose_name = _("Paramètre utilisateur")
        verbose_name_plural = _("Paramètres utilisateurs")
        ordering = ["-created_at"]

    def __str__(self):
        return _("Paramètres de %(email)s") % {"email": self.user.email}

    def _normalize_language(self, value):
        default = (settings.LANGUAGE_CODE or "fr").lower().replace("_", "-").strip()[:10]
        if not value:
            return default

        value = value.lower().replace("_", "-").strip()[:10]
        valid_languages = {code.lower().replace("_", "-") for code, _ in settings.LANGUAGES}

        # autoriser "fr-fr" si "fr" existe
        if value not in valid_languages and value.split("-")[0] in valid_languages:
            return value.split("-")[0]

        return value if value in valid_languages else default

    def save(self, *args, **kwargs):
        self.language = self._normalize_language(self.language)
        super().save(*args, **kwargs)







# # accounts_users/models/users_settings.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone


# class UserSettings(models.Model):
#     """
#     Paramètres utilisateur.
#     Langue normalisée automatiquement (robuste, sans erreur bloquante).
#     """

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="settings",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # PRÉFÉRENCES
#     # ======================================================
#     receive_newsletter = models.BooleanField(
#         _("Recevoir la newsletter"),
#         default=True,
#     )

#     dark_mode = models.BooleanField(
#         _("Mode sombre activé"),
#         default=False,
#     )

#     language = models.CharField(
#         _("Langue préférée"),
#         max_length=10,  # fr, en, fr-fr, en-us
#         choices=settings.LANGUAGES,
#         default=settings.LANGUAGE_CODE,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(
#         _("Créé le"),
#         default=timezone.now,
#         editable=False,
#     )

#     updated_at = models.DateTimeField(
#         _("Mis à jour le"),
#         auto_now=True,
#     )

#     # ======================================================
#     # META
#     # ======================================================
#     class Meta:
#         verbose_name = _("Paramètre utilisateur")
#         verbose_name_plural = _("Paramètres utilisateurs")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"Paramètres de {self.user.email}"

#     # ======================================================
#     # LANGUAGE NORMALIZATION (SAFE)
#     # ======================================================
#     def _normalize_language(self, value):
#         if not value:
#             return settings.LANGUAGE_CODE

#         value = value.lower().replace("_", "-").strip()[:10]

#         valid_languages = {code.lower() for code, _ in settings.LANGUAGES}

#         return value if value in valid_languages else settings.LANGUAGE_CODE

#     # ======================================================
#     # SAVE OVERRIDE
#     # ======================================================
#     def save(self, *args, **kwargs):
#         self.language = self._normalize_language(self.language)
#         super().save(*args, **kwargs)







# # accounts_users/models/users_settings.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone


# class UserSettings(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='settings',
#         verbose_name=_("Utilisateur")
#     )

#     receive_newsletter = models.BooleanField(
#         _("Recevoir la newsletter"),
#         default=True
#     )
#     dark_mode = models.BooleanField(
#         _("Mode sombre activé"),
#         default=False
#     )
#     language = models.CharField(
#     _("Langue préférée"),
#     max_length=10,
#     choices=settings.LANGUAGES,
#     default=settings.LANGUAGE_CODE,
#     )

#     # language = models.CharField(
#     #     _("Langue préférée"),
#     #     max_length=10,
#     #     choices=[
#     #         ('fr', _("Français")),
#     #         ('en', _("Anglais")),
#     #     ],
#     #     default='fr'
#     # )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         default=timezone.now,
#         editable=False
#     )
#     updated_at = models.DateTimeField(
#         _("Mis à jour le"),
#         auto_now=True
#     )

#     class Meta:
#         verbose_name = _("Paramètre utilisateur")
#         verbose_name_plural = _("Paramètres utilisateurs")
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Paramètres de {self.user.email}"
#         # return f"Paramètres de {self.user}"





## accounts_users/models/users_settings.py -> 01/07
# from django.db import models
# from django.conf import settings

# class UserSettings(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     language = models.CharField(max_length=10, default='fr')
#     notifications_enabled = models.BooleanField(default=True)

#     def __str__(self):
#         return f"Settings for {self.user.email}"
