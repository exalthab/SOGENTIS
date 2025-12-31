# accounts_users/models/users_profile.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from accounts_users.models.base import TimeStampedModel


class UserProfile(TimeStampedModel):
    """
    Profil utilisateur SOCIAL – identité de base.

    - Informations personnelles
    - Téléphone principal normalisé
    - AUCUNE logique de workflow (validation, statut, codes)
    """

    # ======================================================
    # LIEN UTILISATEUR
    # ======================================================
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Utilisateur"),
    )

    # ======================================================
    # CONTACT PRINCIPAL
    # ======================================================
    phone_number = PhoneNumberField(
        _("Numéro de téléphone"),
        region="SN",  # Sénégal par défaut (plus cohérent)
        blank=False,
        default="",
        help_text=_(
            "Numéro avec indicatif international. Exemple : +221771234567"
        ),
    )

    # ======================================================
    # IDENTITÉ
    # ======================================================
    last_name = models.CharField(_("Nom"), max_length=100, blank=True, default="")
    first_name = models.CharField(_("Prénom"), max_length=100, blank=True, default="")
    middle_names = models.CharField(_("Autres prénoms"), max_length=150, blank=True, default="")
    nickname = models.CharField(_("Surnom"), max_length=100, blank=True, default="")

    # ======================================================
    # MESSAGE LIBRE
    # ======================================================
    message = models.TextField(_("Message"), blank=True, default="")

    # ======================================================
    # META
    # ======================================================
    class Meta:
        verbose_name = _("Profil utilisateur (social)")
        verbose_name_plural = _("Profils utilisateurs (sociaux)")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
        ]

    def __str__(self):
        full_name = " ".join(filter(None, [self.last_name, self.first_name]))
        return full_name or self.user.get_username()




# # accounts_users/models/users_profile.py
# from django.conf import settings
# from django.db import models
# from phonenumber_field.modelfields import PhoneNumberField

# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.base import TimeStampedModel


# class UserProfile(TimeStampedModel):
#     """
#     Profil utilisateur SOCIAL / ONG
#     (membre, volontaire, donateur, institution).
#     """

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="profile",
#         verbose_name=_("Utilisateur"),
#     )
#     phone_number = PhoneNumberField(region="FR", blank=True, null=True)  # `region` par défaut à "FR" (France)

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     last_name = models.CharField(_("Nom"), max_length=100, blank=True, null=True)
#     first_name = models.CharField(_("Prénom"), max_length=100, blank=True, null=True)
#     middle_names = models.CharField(_("Autres prénoms"), max_length=150, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)

#     # ======================================================
#     # CONTACT
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30, blank=True,null=True)
#     message = models.TextField(_("Message"), blank=True, null=True)

#     # ======================================================
#     # RÔLES & STATUT
#     # ======================================================
#     membership_role = models.ForeignKey(
#         "accounts_users.MembershipRole",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="profiles",
#         verbose_name=_("Rôle d’adhésion"),
#     )

#     status = models.CharField(
#         _("Statut"),
#         max_length=30,
#         choices=[
#             ("pending", _("En attente")),
#             ("active", _("Actif")),
#             ("suspended", _("Suspendu")),
#         ],
#         default="pending",
#     )

#     # ======================================================
#     # CODES SYSTÈME
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code d’enregistrement social"),
#         max_length=50,
#         unique=True,
#         blank=True,
#         null=True,
#         editable=False,
#     )

#     def __str__(self):
#         full = f"{self.last_name} {self.first_name}".strip()
#         return full or str(self.user)
