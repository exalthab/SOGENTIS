# accounts_users/models/admin_role.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class AdminRole(models.Model):
    label = models.CharField(_("Nom du rôle admin"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    permissions = models.ManyToManyField("auth.Permission", verbose_name=_("Permissions"), blank=True)

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        verbose_name = _("Rôle administrateur")
        verbose_name_plural = _("Rôles administrateurs")
        ordering = ["label"]

    def __str__(self):
        return self.label



## accounts_users/models/admin_role.py -> 01/07

# from django.contrib.auth.models import Group

# def create_admin_roles():
#     roles = ['SuperAdmin', 'MembresManager', 'DonsManager']
#     for role in roles:
#         Group.objects.get_or_create(name=role)
