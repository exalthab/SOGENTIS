# accounts_users/models/economic/client_profile.py
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel
from accounts_users.models.users_economic_profile import UserEconomicProfile


class ClientProfile(TimeStampedModel):
    """
    Profil économique – Client (B2C)

    - Ne duplique pas l'identité (dans UserEconomicProfile)
    - Peut stocker une adresse de livraison "préférée" (optionnelle)
    """

    profile = models.OneToOneField(
        UserEconomicProfile,
        on_delete=models.CASCADE,
        related_name="client_profile",
        verbose_name=_("Profil économique"),
    )

    # Adresse de livraison préférée (optionnelle)
    address = models.CharField(_("Adresse (livraison)"), max_length=255, blank=True, default="")
    city = models.CharField(_("Ville (livraison)"), max_length=100, blank=True, default="")
    postal_code = models.CharField(_("Code postal"), max_length=20, blank=True, default="")

    # Préférences / marketing (optionnel)
    preferred_currency = models.CharField(_("Devise préférée"), max_length=10, blank=True, default="")
    accepts_marketing = models.BooleanField(_("Accepte les offres marketing"), default=True)

    class Meta:
        verbose_name = _("Profil client")
        verbose_name_plural = _("Profils clients")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        email = getattr(getattr(self.profile, "user", None), "email", "—")
        return _("Client – %(user)s") % {"user": email}

    # -------- Helpers --------
    @property
    def shipping_address_resolved(self) -> str:
        """
        Adresse de livraison : priorité au ClientProfile, sinon fallback sur UserEconomicProfile.address
        """
        if self.address.strip():
            return self.address.strip()
        return (getattr(self.profile, "address", "") or "").strip()

    @property
    def shipping_city_resolved(self) -> str:
        if self.city.strip():
            return self.city.strip()
        return (getattr(self.profile, "city_of_residence", "") or "").strip()





# # accounts_users/models/economic/client_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.users_economic_profile import UserEconomicProfile


# class ClientProfile(TimeStampedModel):
#     """
#     Profil économique – Client (B2C)

#     - Ne duplique PAS les infos personnelles
#     - S’appuie sur UserEconomicProfile
#     """

#     profile = models.OneToOneField(
#         UserEconomicProfile,
#         on_delete=models.CASCADE,
#         related_name="client_profile",
#         verbose_name=_("Profil économique"),
#     )

#     address = models.CharField(_("Adresse"), max_length=255)
#     city = models.CharField(_("Ville"), max_length=100)
#     postal_code = models.CharField(_("Code postal"), max_length=20, blank=True)

#     class Meta:
#         verbose_name = _("Profil client")
#         verbose_name_plural = _("Profils clients")

#     def __str__(self):
#         return _("Client – %(user)s") % {"user": getattr(self.profile.user, "email", "—")}






# # accounts_users/models/economic/client_profile.py 30/12/2025
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.users_economic_profile import UserEconomicProfile


# class ClientProfile(TimeStampedModel):
#     """
#     Profil économique – Client (B2C)

#     - Ne duplique PAS les infos personnelles
#     - S’appuie sur UserEconomicProfile
#     """

#     profile = models.OneToOneField(
#         UserEconomicProfile,
#         on_delete=models.CASCADE,
#         related_name="client_profile",
#         verbose_name=_("Profil économique"),
#     )

#     address = models.CharField(_("Adresse"), max_length=255)
#     city = models.CharField(_("Ville"), max_length=100)
#     postal_code = models.CharField(_("Code postal"), max_length=20, blank=True)

#     class Meta:
#         verbose_name = _("Profil client")
#         verbose_name_plural = _("Profils clients")

#     def __str__(self):
#         return _("Client – %(user)s") % {"user": self.profile.user.email}






# # accounts_users/models/economic/client_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_economic_profile import UserProfile


# class ClientProfile(models.Model):
#     """
#     Profil économique – Client (B2C)

#     - Ne duplique PAS l’adresse
#     - Utilise uniquement UserProfile pour les infos personnelles
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="client_profile",
#         verbose_name=_("Profil utilisateur"),
#     )
    
#     address = models.CharField(
#         _("Adresse"),
#         max_length=255,
#     )

#     city = models.CharField(
#         _("Ville"),
#         max_length=100,
#     )

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#     )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     class Meta:
#         verbose_name = _("Profil client")
#         verbose_name_plural = _("Profils clients")

#     def __str__(self):
#         return f"Client – {self.profile}"




# # accounts_users/models/economic/client_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# class ClientProfile(models.Model):
#     """
#     Profil économique – Client (B2C)
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="client_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     address = models.CharField(
#         _("Adresse"),
#         max_length=255,
#     )

#     city = models.CharField(
#         _("Ville"),
#         max_length=100,
#     )

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#     )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     class Meta:
#         verbose_name = _("Profil client")
#         verbose_name_plural = _("Profils clients")

#     def __str__(self):
#         return f"Client – {self.profile}"




# # accounts_users/models/economic/client_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# class ClientProfile(models.Model):
#     """
#     Profil économique – Client (B2C)
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="client_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     address = models.CharField(
#         _("Adresse"),
#         max_length=255,
#     )
#     city = models.CharField(
#         _("Ville"),
#         max_length=100,
#     )
#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Profil client")
#         verbose_name_plural = _("Profils clients")

#     def __str__(self):
#         return f"Client – {self.profile.full_name}"
