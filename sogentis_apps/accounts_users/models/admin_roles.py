# accounts_users/models/admin_roles.py
from django.db import models
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel


class AdminRole(TimeStampedModel):
    """
    Rôle administrateur (back-office).
    Utilisable si tu veux gérer des ensembles de permissions hors Groups.
    """

    label = models.CharField(_("Nom du rôle admin"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)

    permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("Permissions"),
        blank=True,
        related_name="custom_admin_roles",
    )

    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        verbose_name = _("Rôle administrateur")
        verbose_name_plural = _("Rôles administrateurs")
        ordering = ["label"]
        constraints = [
            models.UniqueConstraint(Upper("label"), name="uniq_admin_role_label_ci")
        ]

    def save(self, *args, **kwargs):
        if self.label:
            self.label = self.label.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label










# # /accounts_users/models/admin_roles.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.db.models.functions import Upper


# class AdminRole(models.Model):
#     """
#     Rôle administrateur (permissions back-office).
#     """

#     label = models.CharField(
#         _("Nom du rôle admin"),
#         max_length=100,
#         unique=True,
#     )

#     description = models.TextField(
#         _("Description"),
#         blank=True,
#     )

#     permissions = models.ManyToManyField(
#         "auth.Permission",
#         verbose_name=_("Permissions"),
#         blank=True,
#     )

#     is_active = models.BooleanField(
#         _("Actif"),
#         default=True,
#     )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     updated_at = models.DateTimeField(
#         _("Mis à jour le"),
#         auto_now=True,
#     )

#     class Meta:
#         verbose_name = _("Rôle administrateur")
#         verbose_name_plural = _("Rôles administrateurs")
#         ordering = ["label"]
#         constraints = [
#             models.UniqueConstraint(
#                 Upper("label"),
#                 name="uniq_admin_role_label_ci",
#             )
#         ]

#     def save(self, *args, **kwargs):
#         if self.label:
#             self.label = self.label.strip()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.label





# # accounts_users/models/admin_role.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class AdminRole(models.Model):
#     label = models.CharField(_("Nom du rôle admin"), max_length=100, unique=True)
#     description = models.TextField(_("Description"), blank=True)
#     permissions = models.ManyToManyField("auth.Permission", verbose_name=_("Permissions"), blank=True)

#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     is_active = models.BooleanField(_("Actif"), default=True)

#     class Meta:
#         verbose_name = _("Rôle administrateur")
#         verbose_name_plural = _("Rôles administrateurs")
#         ordering = ["label"]

#     def __str__(self):
#         return self.label



## accounts_users/models/admin_role.py -> 01/07

# from django.contrib.auth.models import Group

# def create_admin_roles():
#     roles = ['SuperAdmin', 'MembresManager', 'DonsManager']
#     for role in roles:
#         Group.objects.get_or_create(name=role)
