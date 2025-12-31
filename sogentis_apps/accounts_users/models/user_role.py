# accounts_users/models/user_role.py
from django.db import models
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel


class UserRole(TimeStampedModel):
    """
    Rôle ADMIN (back-office) — admin / superuser / moderator
    (Utilisé si tu ne veux pas uniquement Group/Permission)
    """

    CODE_CHOICES = [
        ("admin", _("Administrateur")),
        ("superuser", _("Super-utilisateur")),
        ("moderator", _("Modérateur")),
    ]

    code = models.CharField(
        _("Code interne"),
        max_length=20,
        unique=True,
        choices=CODE_CHOICES,
        default="admin",
    )

    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        verbose_name = _("Rôle administratif")
        verbose_name_plural = _("Rôles administratifs")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(Upper("code"), name="uniq_user_role_code_ci")
        ]

    def __str__(self):
        return self.get_code_display()


class EconomicRole(models.TextChoices):
    CLIENT = "CLIENT", _("Client")
    VENDOR = "VENDOR", _("Vendeur")
    B2B = "B2B", _("Entreprise / B2B")







# # accounts_users/models/user_role.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone


# class UserRole(models.Model):
#     ROLE_CHOICES = [
#         ('admin', _("Administrateur")),
#         ('superuser', _("Super-utilisateur")),
#         ('moderator', _("Modérateur")),
#     ]

#     role = models.CharField(max_length=255, null=True, blank=True)

#     code = models.CharField(
#         _("Code interne"),
#         max_length=50,
#         choices=ROLE_CHOICES,
#         unique=True,
#         default='admin'
#     )
#     label = models.CharField(
#         _("Nom du rôle"),
#         max_length=100,
#         default=_("Administrateur")
#     )
#     is_active = models.BooleanField(
#         _("Actif"),
#         default=True
#     )

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
#         verbose_name = _("Rôle administratif")
#         verbose_name_plural = _("Rôles administratifs")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.get_code_display()

# class EconomicRole(models.TextChoices):
#     CLIENT = "CLIENT", _("Client")
#     VENDOR = "VENDOR", _("Vendeur")
#     B2B = "B2B", _("Entreprise / B2B")







## accounts_users/models/user_role.py ->01/07
# # Modèle est pour les rôles du profil utilisateur, pas le dashboard
# from django.db import models

# class UserRole(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     slug = models.SlugField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name
