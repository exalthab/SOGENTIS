# accounts_users/models/membership_role.py 
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class MembershipRole(models.Model):
    ROLE_CHOICES = [
        ('MEMBER', _("Membre")),
        ('VOLUNTEER', _("Volontaire")),
        ('SPONSOR', _("Donateur")),
        ('INSTITUTION', _("Institution")),
    ]

    code = models.CharField(
        _("Code interne"),
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
        default='MEMBER'  # ✅ Obligatoire pour la migration
    )
    label = models.CharField(
        _("Libellé"),
        max_length=255,
        default=_("Membre")
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True
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
        verbose_name = _("Rôle d’adhésion")
        verbose_name_plural = _("Rôles d’adhésion")
        ordering = ["label"]

    def __str__(self):
        return self.get_code_display()  # ✅ Affiche le libellé depuis choices




# # accounts_users/models/membership_role.py -> 01/07

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# class MembershipRole(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)

#     class Meta:
#         verbose_name = _("Rôle d’adhésion")
#         verbose_name_plural = _("Rôles d’adhésion")

#     def __str__(self):
#         return self.name
