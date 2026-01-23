# accounts_users/models/accounts_users.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class LegacyUserProfile(models.Model):
    """
    ⚠️ Legacy (à migrer / supprimer plus tard).
    Ne doit PAS s’appeler UserProfile (conflit).
    Ne doit PAS utiliser related_name="profile" (conflit).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="legacy_profile",
    )

    last_name = models.CharField(_("Nom"), max_length=100)
    first_name = models.CharField(_("Prénom"), max_length=100)
    middle_names = models.CharField(_("Autres prénoms"), max_length=150, blank=True)
    nickname = models.CharField(_("Surnom"), max_length=100, blank=True)

    phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
    message = models.TextField(_("Message"), blank=True)

    membership_role = models.ForeignKey(
        "accounts_users.MembershipRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    economic_role = models.ForeignKey(
        "accounts_users.UserRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        _("Statut"),
        max_length=30,
        choices=[
            ("pending", _("En attente")),
            ("active", _("Actif")),
            ("suspended", _("Suspendu")),
        ],
        default="pending",
    )

    social_registration_code = models.CharField(
        _("Code d’enregistrement social"),
        max_length=50,
        unique=True,
        editable=False,
    )

    economic_registration_code = models.CharField(
        _("Code d’enregistrement économique"),
        max_length=50,
        unique=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()









# # accounts_users/models/accounts_users.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _


# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="profile",
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     last_name = models.CharField(_("Nom"), max_length=100)
#     first_name = models.CharField(_("Prénom"), max_length=100)
#     middle_names = models.CharField(_("Autres prénoms"), max_length=150, blank=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True)

#     # ======================================================
#     # CONTACT
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
#     message = models.TextField(_("Message"), blank=True)

#     # ======================================================
#     # RÔLES & STATUT
#     # ======================================================
#     membership_role = models.ForeignKey(
#         "accounts_users.MembershipRole",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#     )

#     economic_role = models.ForeignKey(
#         "accounts_users.UserRole",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
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
#     # CODES SYSTÈME ✅ (CE QUI MANQUAIT)
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code d’enregistrement social"),
#         max_length=50,
#         unique=True,
#         editable=False,
#     )

#     economic_registration_code = models.CharField(
#         _("Code d’enregistrement économique"),
#         max_length=50,
#         unique=True,
#         editable=False,
#     )

#     # ======================================================
#     # MÉTADONNÉES
#     # ======================================================
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.last_name} {self.first_name}"
