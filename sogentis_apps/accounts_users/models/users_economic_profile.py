# accounts_users/models/users_economic_profile.py
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from accounts_users.models.base import TimeStampedModel
from accounts_users.models.user_role import EconomicRole


def profile_picture_upload_path(instance, filename):
    return f"users/profile_pictures/{instance.user_id}/{filename}"


class UserEconomicProfile(TimeStampedModel):
    """
    Profil utilisateur ÉCONOMIQUE / Plateforme :
    CLIENT / VENDOR / B2B

    - Profil racine économique
    - Utilisé par ClientProfile / VendorProfile / CompanyProfile
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="economic_profile",
        verbose_name=_("Utilisateur"),
    )

    # =========================
    # IDENTITÉ
    # =========================
    first_name = models.CharField(_("Prénom"), max_length=150, blank=True)
    last_name = models.CharField(_("Nom"), max_length=150, blank=True)
    middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True)
    nickname = models.CharField(_("Surnom"), max_length=100, blank=True)

    date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
    place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True)

    # =========================
    # RÉSIDENCE
    # =========================
    country_of_residence = CountryField(_("Pays de résidence"), blank=True)
    city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True)
    address = models.TextField(_("Adresse"), blank=True)

    country_of_birth = CountryField(_("Pays de naissance"), blank=True)

    # =========================
    # CONTACT / PROFESSION
    # =========================
    phone = PhoneNumberField(_("Téléphone"), region="SN", blank=True, default="")
    profession = models.CharField(_("Profession"), max_length=150, blank=True)
    function = models.CharField(_("Fonction"), max_length=150, blank=True)
    message = models.TextField(_("Message"), blank=True)

    # =========================
    # ÉCONOMIQUE
    # =========================
    economic_role = models.CharField(
        _("Rôle économique"),
        max_length=20,
        choices=EconomicRole.choices,
        blank=True,
    )

    economic_registration_code = models.CharField(
        _("Code économique"),
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        help_text=_("Généré automatiquement"),
    )

    # =========================
    # FICHIER
    # =========================
    profile_picture = models.ImageField(
        _("Photo de profil"),
        upload_to=profile_picture_upload_path,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Profil économique")
        verbose_name_plural = _("Profils économiques")
        ordering = ["-created_at"]

    def __str__(self):
        full_name = " ".join(filter(None, [self.last_name, self.first_name])).strip()
        return full_name or getattr(self.user, "email", str(self.user_id))

    def _generate_economic_code(self) -> str:
        role = (self.economic_role or "EC").upper()
        token = uuid.uuid4().hex[:10].upper()
        return f"EC-{role}-{token}"

    def save(self, *args, **kwargs):
        if not self.economic_registration_code:
            self.economic_registration_code = self._generate_economic_code()
        super().save(*args, **kwargs)








# # accounts_users/models/users_economic_profile.py 30/12/2025
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_countries.fields import CountryField

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.user_role import EconomicRole



# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user_id}/{filename}"


# class UserEconomicProfile(TimeStampedModel):
#     """
#     Profil utilisateur ÉCONOMIQUE / Plateforme :
#     CLIENT / VENDOR / B2B

#     - Profil racine économique
#     - Utilisé par ClientProfile / VendorProfile / CompanyProfile
#     """

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="economic_profile",
#         verbose_name=_("Utilisateur"),
#     )

#     # =========================
#     # IDENTITÉ
#     # =========================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True)

#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True)

#     # =========================
#     # RÉSIDENCE
#     # =========================
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True)
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True)
#     address = models.TextField(_("Ad resse"), blank=True)

#     country_of_birth = CountryField(_("Pays de naissance"), blank=True)

#     # =========================
#     # CONTACT / PROFESSION
#     # =========================
#     phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True)
#     message = models.TextField(_("Message"), blank=True)
#     # judicial_record = models.BooleanField(_("Casier judiciaire"), default=False)

#     # =========================
#     # ÉCONOMIQUE
#     # =========================
#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=50,
#         unique=True,
#         blank=True,
#         null=True,
#         editable=False,
#         help_text=_("Généré automatiquement"),
#     )

#     # =========================
#     # FICHIER
#     # =========================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     class Meta:
#         verbose_name = _("Profil économique")
#         verbose_name_plural = _("Profils économiques")
#         ordering = ["-created_at"]

#     def __str__(self):
#         full_name = " ".join(filter(None, [self.last_name, self.first_name]))
#         return full_name or self.user.email






# # accounts_users/models/users_economic_profile.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_countries.fields import CountryField

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.user_role import EconomicRole


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user_id}/{filename}"


# class UserEconomicProfile(TimeStampedModel):
#     """
#     Profil utilisateur ÉCONOMIQUE / Plateforme :
#     CLIENT / VENDOR / B2B

#     - Profil racine économique
#     - Utilisé par ClientProfile / VendorProfile / CompanyProfile
#     """

#     # ======================================================
#     # UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="economic_profile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True)

#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True)
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True)
#     address = models.TextField(_("Adresse"), blank=True)

#     country_of_birth = CountryField(_("Pays de naissance"), blank=True)

#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True)
#     message = models.TextField(_("Message"), blank=True)
#     judicial_record = models.BooleanField(_("Casier judiciaire"), default=False)

#     # ======================================================
#     # ÉCONOMIQUE
#     # ======================================================
#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=50,
#         unique=True,
#         blank=True,
#         null=True,
#         editable=False,
#         help_text=_("Généré automatiquement"),
#     )

#     # ======================================================
#     # FICHIER
#     # ======================================================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # META
#     # ======================================================
#     class Meta:
#         verbose_name = _("Profil économique")
#         verbose_name_plural = _("Profils économiques")
#         ordering = ["-created_at"]

#     # ======================================================
#     # STRING
#     # ======================================================
#     def __str__(self):
#         full_name = " ".join(filter(None, [self.last_name, self.first_name]))
#         return full_name or self.user.email







# # accounts_users/models/users_economic_profile.py
# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_countries.fields import CountryField

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.user_role import EconomicRole


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user_id}/{filename}"


# class UserEconomicProfile(TimeStampedModel):
#     """
#     Profil utilisateur ÉCONOMIQUE / Plateforme :
#     CLIENT / VENDOR / B2B
#     """

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="economic_profile",
#         verbose_name=_("Utilisateur"),
#     )

#     # Identité
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)

#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # Résidence
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # Contact / pro
#     phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)
#     message = models.TextField(_("Message"), blank=True)
#     judicial_record = models.BooleanField(_("Casier judiciaire"), default=False)

#     # Économique
#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=50,
#         unique=True,
#         blank=True,
#         null=True,
#         editable=False,
#     )

#     # Fichier
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     class Meta:
#         verbose_name = _("Profil économique")
#         verbose_name_plural = _("Profils économiques")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.last_name or ''} {self.first_name or ''}".strip() or str(self.user)

#     def _normalize_country(self, value):
#         if not value:
#             return None
#         if hasattr(value, "code"):
#             return value.code.upper()
#         if isinstance(value, str):
#             value = value.strip().upper()
#             return value if len(value) == 2 else None
#         return None

#     def clean(self):
#         for field in ("country_of_birth", "country_of_residence"):
#             value = getattr(self, field)
#             if value and self._normalize_country(value) is None:
#                 raise ValidationError({field: _("Pays invalide : code ISO alpha-2 requis.")})

#     def save(self, *args, **kwargs):
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)
#         super().save(*args, **kwargs)






# # accounts_users/models/users_economic_profile.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
# from django_countries.fields import CountryField

# from accounts_users.models.user_role import UserRole, EconomicRole


# # ======================================================
# # UPLOAD PATHS
# # ======================================================
# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# # ======================================================
# # MODEL
# # ======================================================
# class UserProfile(models.Model):
#     """
#     Profil utilisateur PLATEFORME.

#     - Concerne uniquement :
#         • Client
#         • Vendeur
#         • Entreprise (B2B)
#     - Ne contient AUCUNE logique sociale / ONG
#     """

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)

#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)

#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)
#     membership_role = models.CharField(max_length=50)
#     message = models.TextField(blank=True)
#     judicial_record = models.BooleanField(default=False)
#     # ======================================================
#     # PLATEFORME / ÉCONOMIQUE
#     # ======================================================
#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Rôle administratif"),
#     )

#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # FICHIERS
#     # ======================================================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     # ======================================================
#     # META
#     # ======================================================
#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateurs")
#         ordering = ["-created_at"]

#     # ======================================================
#     # STRING
#     # ======================================================
#     def __str__(self):
#         return f"{self.last_name or ''} {self.first_name or ''}".strip()

#     # ======================================================
#     # COUNTRY NORMALIZATION
#     # ======================================================
#     def _normalize_country(self, value):
#         if not value:
#             return None
#         if hasattr(value, "code"):
#             return value.code.upper()
#         if isinstance(value, str):
#             value = value.strip().upper()
#             if len(value) == 2:
#                 return value
#         return None

#     # ======================================================
#     # VALIDATION
#     # ======================================================
#     def clean(self):
#         for field in ("country_of_birth", "country_of_residence"):
#             value = getattr(self, field)
#             if value and self._normalize_country(value) is None:
#                 raise ValidationError({
#                     field: _("Pays invalide : code ISO alpha-2 requis.")
#                 })

#     # ======================================================
#     # SAVE
#     # ======================================================
#     def save(self, *args, **kwargs):
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)
#         super().save(*args, **kwargs)








# # accounts_users/models/users_profile.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
# from django_countries.fields import CountryField

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole, EconomicRole


# # ======================================================
# # UPLOAD PATHS
# # ======================================================
# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# # ======================================================
# # MODEL
# # ======================================================
# class UserProfile(models.Model):
#     """
#     Profil utilisateur central.
#     Sécurisé contre les erreurs de code pays (ISO alpha-2).
#     """

#     # ======================================================
#     # STATUT
#     # ======================================================
#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)
#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)

#     # ======================================================
#     # PAYS (ISO ALPHA-2 UNIQUEMENT)
#     # ⚠️ Champ legacy à garder pour migration
#     # ======================================================
#     country = CountryField(_("Pays (legacy)"), blank=True, null=True)
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

#     # ======================================================
#     # FICHIERS
#     # ======================================================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )
#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=False,
#         null=False,
#     )
#     message = models.TextField(_("Message"), blank=True)

#     # ======================================================
#     # RÔLES
#     # ======================================================
#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Rôle administratif"),
#     )
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Type d’adhésion (Social)"),
#     )
#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # CODES
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code social"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )
#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # STATUT
#     # ======================================================
#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     # ======================================================
#     # META
#     # ======================================================
#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateurs")
#         ordering = ["-created_at"]

#     # ======================================================
#     # STRING
#     # ======================================================
#     def __str__(self):
#         return f"{self.last_name or ''} {self.first_name or ''}".strip()

#     # ======================================================
#     # COUNTRY NORMALIZATION AND VALIDATION
#     # ======================================================
#     def _normalize_country(self, value):
#         if not value:
#             return None
#         if hasattr(value, "code"):
#             return value.code.upper()
#         if isinstance(value, str):
#             value = value.strip().upper()
#             if len(value) == 2:
#                 return value
#         return None

#     # ======================================================
#     # VALIDATION DU MODÈLE
#     # ======================================================
#     def clean(self):
#         for field in ("country", "country_of_birth", "country_of_residence"):
#             value = getattr(self, field)
#             if value and self._normalize_country(value) is None:
#                 raise ValidationError({field: _("Pays invalide : code ISO alpha-2 requis.")})

#     # ======================================================
#     # SAVE OVERRIDE
#     # ======================================================
#     def save(self, *args, **kwargs):
#         # Normalisation des pays avant sauvegarde
#         self.country = self._normalize_country(self.country)
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)
#         super().save(*args, **kwargs)







# # accounts_users/models/users_profile.py 21/12/2025 error
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
# from django_countries.fields import CountryField

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole, EconomicRole


# # ======================================================
# # UPLOAD PATHS
# # ======================================================
# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# # ======================================================
# # MODEL
# # ======================================================
# class UserProfile(models.Model):
#     """
#     Profil utilisateur central.
#     Sécurisé définitivement contre les erreurs varchar(2) (CountryField).
#     """

#     # ======================================================
#     # STATUT
#     # ======================================================
#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)
#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)

#     # ======================================================
#     # PAYS (ISO ALPHA-2 UNIQUEMENT)
#     # ⚠️ CHAMP HISTORIQUE – NE PAS SUPPRIMER AVANT MIGRATION
#     # ======================================================
#     country = CountryField(_("Pays (legacy)"), blank=True, null=True)
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

#     # ======================================================
#     # FICHIERS
#     # ======================================================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )
#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )
#     message = models.TextField(_("Message"), blank=True)

#     # ======================================================
#     # RÔLES
#     # ======================================================
#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Rôle administratif"),
#     )
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Type d’adhésion (Social)"),
#     )
#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # CODES
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code social"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )
#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # STATUT
#     # ======================================================
#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     # ======================================================
#     # META
#     # ======================================================
#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateurs")
#         ordering = ["-created_at"]

#     # ======================================================
#     # STRING
#     # ======================================================
#     def __str__(self):
#         return f"{self.last_name or ''} {self.first_name or ''}".strip()

#     # ======================================================
#     # COUNTRY NORMALIZATION
#     # ======================================================
#     def _normalize_country(self, value):
#         if not value:
#             return None
#         if hasattr(value, "code"):
#             return value.code.upper()
#         if isinstance(value, str):
#             value = value.strip().upper()
#             if len(value) == 2:
#                 return value
#         return None

#     # ======================================================
#     # MODEL VALIDATION
#     # ======================================================
#     def clean(self):
#         for field in ("country",):
#             value = getattr(self, field)
#             if value and self._normalize_country(value) is None:
#                 raise ValidationError({field: _("Pays invalide : code ISO alpha-2 requis.")})

#     # ======================================================
#     # SAVE OVERRIDE
#     # ======================================================
#     def save(self, *args, **kwargs):
#         self.country = self._normalize_country(self.country)
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)
#         super().save(*args, **kwargs)






# # accounts_users/models/users_profile.py Novembre 2025
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole

# # Ajout pour la gestion des pays
# from django_countries.fields import CountryField

# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"

# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"

# class UserProfile(models.Model):
#     class Status(models.TextChoices):
#         PENDING = 'pending', _("En attente")
#         APPROVED = 'approved', _("Approuvé")
#         REJECTED = 'rejected', _("Refusé")

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur")
#     )

#     full_name = models.CharField(_("Nom complet"), max_length=255, null=True, blank=True)
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     # Remplace le CharField par le CountryField
#     country = CountryField(verbose_name=_("Pays"), blank=True, null=True)
#     # country = CountryField(blank=True, null=True)

#     message = models.TextField(_("Message"), blank=True)

#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True, null=True
#     )
#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True, null=True
#     )

#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         verbose_name=_("Rôle administratif")
#     )
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         verbose_name=_("Type d’adhésion")
#     )

#     registration_code = models.CharField(
#         _("Code d'inscription"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#         help_text=_("Code unique par type d’adhésion (ex: M001, V001, D001)")
#     )

#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING
#     )

#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateur")
#         ordering = ['-created_at']

#     def __str__(self):
#         return self.full_name or str(self.user)

#     def save(self, *args, **kwargs):
#         if not self.registration_code and self.membership_role:
#             prefix_map = {
#                 'MEMBER': 'M',
#                 'VOLUNTEER': 'V',
#                 'SPONSOR': 'D',
#                 'INSTITUTION': 'I',
#             }
#             prefix = prefix_map.get(self.membership_role.code.upper(), 'X')
#             existing = UserProfile.objects.filter(
#                 membership_role__code=self.membership_role.code
#             ).count() + 1
#             self.registration_code = f"{prefix}{str(existing).zfill(3)}"
#         super().save(*args, **kwargs)








# # accounts_users/models/users_profile.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
# from django_countries.fields import CountryField
# from django_countries.fields import Country

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole, EconomicRole


# # ======================================================
# # UPLOAD PATHS
# # ======================================================

# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# # ======================================================
# # MODEL
# # ======================================================

# class UserProfile(models.Model):
#     """
#     Profil utilisateur central.
#     Sécurisé définitivement contre les erreurs varchar(2) (CountryField).
#     """

#     # ======================================================
#     # STATUT
#     # ======================================================

#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================

#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)

#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # ======================================================
#     # PAYS (ISO ALPHA-2 UNIQUEMENT)
#     # ======================================================

#     # country = CountryField(_("Pays"), blank=True, null=True)
#     # country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)
#     # country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================

#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)
    

#     # ⚠️ CHAMP HISTORIQUE – NE PAS SUPPRIMER AVANT MIGRATION
    
#     country = CountryField(_("Pays (legacy)"), blank=True, null=True,)
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True,)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True,)
    
#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================

#     phone = models.CharField(_("Téléphone"), max_length=30)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

#     # ======================================================
#     # FICHIERS
#     # ======================================================

#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )

#     message = models.TextField(_("Message"), blank=True)

#     # ======================================================
#     # RÔLES
#     # ======================================================

#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Rôle administratif"),
#     )

#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Type d’adhésion (Social)"),
#     )

#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # CODES
#     # ======================================================

#     social_registration_code = models.CharField(
#         _("Code social"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # STATUT
#     # ======================================================

#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================

#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     # ======================================================
#     # META
#     # ======================================================

#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateurs")
#         ordering = ["-created_at"]

#     # ======================================================
#     # STRING
#     # ======================================================

#     def __str__(self):
#         return f"{self.last_name or ''} {self.first_name or ''}".strip()

#     # ======================================================
#     # COUNTRY NORMALIZATION (ANTI varchar(2))
#     # ======================================================

#     def _normalize_country(self, value):
#         """
#         Retourne un code ISO alpha-2 valide ou None.
#         Empêche toute valeur > 2 caractères d'atteindre la DB.
#         """
#         if not value:
#             return None

#         # django-countries Country object
#         if hasattr(value, "code"):
#             return value.code.upper()

#         # string
#         if isinstance(value, str):
#             value = value.strip().upper()
#             if len(value) == 2:
#                 return value

#         return None

#     # ======================================================
#     # MODEL VALIDATION
#     # ======================================================

#     def clean(self):
#         for field in ("country", "country_of_birth", "country_of_residence"):
#             value = getattr(self, field)
#             if value and self._normalize_country(value) is None:
#                 raise ValidationError({
#                     field: _("Pays invalide : code ISO alpha-2 requis.")
#                 })

#     # ======================================================
#     # SAVE OVERRIDE (ULTIMATE SAFETY)
#     # ======================================================

#     def save(self, *args, **kwargs):
#         self.country = self._normalize_country(self.country)
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)

#         super().save(*args, **kwargs)






# # accounts_users/models/users_profile.py (File qui provoque erreur (var(2))21/12/2025

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_countries.fields import CountryField

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole, EconomicRole


# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# class UserProfile(models.Model):
#     """
#     Profil utilisateur central.
#     Sécurisé contre toute valeur invalide (CountryField).
#     """

#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ
#     # ======================================================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)

#     date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # ======================================================
#     # PAYS (ISO alpha-2 UNIQUEMENT)
#     # ======================================================
#     country = CountryField(_("Pays"), blank=True, null=True)

#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)

#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

#     # ======================================================
#     # FICHIERS
#     # ======================================================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )

#     message = models.TextField(_("Message"), blank=True)

#     # ======================================================
#     # RÔLES
#     # ======================================================
#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Rôle administratif"),
#     )

#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Type d’adhésion (Social)"),
#     )

#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # CODES
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code social"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # STATUT
#     # ======================================================
#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateurs")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.last_name or ''} {self.first_name or ''}".strip()

#     # ======================================================
#     # SÉCURISATION DÉFINITIVE (ANTI varchar(2))
#     # ======================================================
#     def _normalize_country(self, value):
#         """
#         Garantit ISO alpha-2 ou NULL.
#         Empêche toute valeur > 2 caractères d'atteindre la DB.
#         """
#         if not value:
#             return None
#         if isinstance(value, str) and len(value) == 2:
#             return value.upper()
#         return None

#     def save(self, *args, **kwargs):

#         # 🔒 Sécurisation ABSOLUE des CountryField
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)

#         super().save(*args, **kwargs)




# # accounts_users/models/users_profile.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_countries.fields import CountryField

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole, EconomicRole


# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# class UserProfile(models.Model):
#     """
#     Profil utilisateur central.
#     Gère :
#     - identité réelle
#     - social
#     - économique
#     - administratif
#     """

#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # IDENTITÉ PERSONNELLE (STRUCTURÉE)
#     # ======================================================
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     # last_name = models.CharField(_("Nom"), max_length=150)
#     # first_name = models.CharField(_("Prénom"), max_length=150)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)

#     date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # ======================================================
#     # RÉSIDENCE
#     # ======================================================
#     country = CountryField(_("Pays"), blank=True, null=True)
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     # country_of_residence = CountryField(_("Pays de résidence"))
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)

#     # ======================================================
#     # CONTACT / PROFESSION
#     # ======================================================
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

#     # ======================================================
#     # FICHIERS
#     # ======================================================
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )

#     message = models.TextField(_("Message"), blank=True)

#     # ======================================================
#     # RÔLES
#     # ======================================================
#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Rôle administratif"),
#     )

#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Type d’adhésion (Social)"),
#     )

#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # CODES D’INSCRIPTION
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code social"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     economic_registration_code = models.CharField(
#         _("Code économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # STATUT
#     # ======================================================
#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateurs")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.last_name} {self.first_name}"

#     # ======================================================
#     # GÉNÉRATION DE CODES ROBUSTE
#     # ======================================================
#     def _generate_incremental_code(self, queryset, field_name, prefix):
#         last = (
#             queryset.exclude(**{f"{field_name}__isnull": True})
#             .order_by(f"-{field_name}")
#             .first()
#         )
#         if not last:
#             return f"{prefix}001"

#         try:
#             number = int(getattr(last, field_name)[1:])
#         except Exception:
#             number = 0

#         return f"{prefix}{str(number + 1).zfill(3)}"

#     def save(self, *args, **kwargs):

#         if not self.social_registration_code and self.membership_role:
#             prefix = {
#                 "MEMBER": "M",
#                 "VOLUNTEER": "V",
#                 "SPONSOR": "D",
#                 "INSTITUTION": "I",
#             }.get(self.membership_role.code, "X")

#             self.social_registration_code = self._generate_incremental_code(
#                 UserProfile.objects.filter(membership_role__code=self.membership_role.code),
#                 "social_registration_code",
#                 prefix,
#             )

#         if not self.economic_registration_code and self.economic_role:
#             prefix = {
#                 "CLIENT": "C",
#                 "VENDOR": "V",
#                 "B2B": "B",
#             }.get(self.economic_role, "X")

#             self.economic_registration_code = self._generate_incremental_code(
#                 UserProfile.objects.filter(economic_role=self.economic_role),
#                 "economic_registration_code",
#                 prefix,
#             )

#         super().save(*args, **kwargs)






# # accounts_users/models/users_profile.py
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from django_countries.fields import CountryField

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole, EconomicRole


# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# class UserProfile(models.Model):
#     """
#     Profil utilisateur central.
#     Sépare clairement :
#     - Social (membership_role)
#     - Économique (economic_role)
#     - Administratif (role)
#     """

#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # ======================================================
#     # LIEN UTILISATEUR
#     # ======================================================
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     # ======================================================
#     # INFOS GÉNÉRALES
#     # ======================================================
#     full_name = models.CharField(_("Nom complet"), max_length=255)
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     country = CountryField(verbose_name=_("Pays"))
#     message = models.TextField(_("Message"), blank=True)

#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )

#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # RÔLES
#     # ======================================================
#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Rôle administratif"),
#     )

#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Type d’adhésion (Social)"),
#     )

#     economic_role = models.CharField(
#         _("Rôle économique"),
#         max_length=20,
#         choices=EconomicRole.choices,
#         blank=True,
#         null=True,
#     )

#     # ======================================================
#     # CODES D’INSCRIPTION
#     # ======================================================
#     social_registration_code = models.CharField(
#         _("Code d'inscription social"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#         help_text=_("Code social unique (ex: M001, V002, D015)"),
#     )

#     economic_registration_code = models.CharField(
#         _("Code d'inscription économique"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#         help_text=_("Code économique unique (ex: C001, V010, B003)"),
#     )

#     # ======================================================
#     # STATUT
#     # ======================================================
#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     # ======================================================
#     # TIMESTAMPS
#     # ======================================================
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateur")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.full_name or str(self.user)

#     # ======================================================
#     # MÉTHODES INTERNES
#     # ======================================================
#     def _generate_incremental_code(self, queryset, field_name, prefix):
#         """
#         Génère un code incrémental robuste basé sur le dernier code existant.
#         Exemple : C001 → C002
#         """
#         last_obj = (
#             queryset
#             .exclude(**{f"{field_name}__isnull": True})
#             .order_by(f"-{field_name}")
#             .first()
#         )

#         if not last_obj:
#             return f"{prefix}001"

#         last_code = getattr(last_obj, field_name)
#         try:
#             last_number = int(last_code[1:])
#         except (ValueError, TypeError):
#             last_number = 0

#         return f"{prefix}{str(last_number + 1).zfill(3)}"

#     # ======================================================
#     # SAVE
#     # ======================================================
#     def save(self, *args, **kwargs):

#         # -----------------------------
#         # SOCIAL
#         # -----------------------------
#         if not self.social_registration_code and self.membership_role:
#             prefix_map = {
#                 "MEMBER": "M",
#                 "VOLUNTEER": "V",
#                 "SPONSOR": "D",
#                 "INSTITUTION": "I",
#             }
#             prefix = prefix_map.get(self.membership_role.code, "X")

#             self.social_registration_code = self._generate_incremental_code(
#                 queryset=UserProfile.objects.filter(
#                     membership_role__code=self.membership_role.code
#                 ),
#                 field_name="social_registration_code",
#                 prefix=prefix,
#             )

#         # -----------------------------
#         # ÉCONOMIQUE
#         # -----------------------------
#         if not self.economic_registration_code and self.economic_role:
#             prefix_map = {
#                 "CLIENT": "C",
#                 "VENDOR": "V",
#                 "B2B": "B",
#             }
#             prefix = prefix_map.get(self.economic_role, "X")

#             self.economic_registration_code = self._generate_incremental_code(
#                 queryset=UserProfile.objects.filter(
#                     economic_role=self.economic_role
#                 ),
#                 field_name="economic_registration_code",
#                 prefix=prefix,
#             )

#         super().save(*args, **kwargs)




# # accounts_users/models/users_profile.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from django_countries.fields import CountryField

# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole


# def judicial_record_upload_path(instance, filename):
#     return f"users/judicial_records/{instance.user.id}/{filename}"


# def profile_picture_upload_path(instance, filename):
#     return f"users/profile_pictures/{instance.user.id}/{filename}"


# class UserProfile(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="userprofile",
#         verbose_name=_("Utilisateur"),
#     )

#     full_name = models.CharField(
#         _("Nom complet"),
#         max_length=255,
#     )
#     phone = models.CharField(
#         _("Téléphone"),
#         max_length=30,
#     )
#     country = CountryField(
#         verbose_name=_("Pays"),
#     )
#     message = models.TextField(
#         _("Message"),
#         blank=True,
#     )

#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )
#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to=judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )

#     role = models.ForeignKey(
#         UserRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Rôle administratif"),
#     )
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Type d’adhésion"),
#     )

#     registration_code = models.CharField(
#         _("Code d'inscription"),
#         max_length=10,
#         unique=True,
#         blank=True,
#         null=True,
#         help_text=_(
#             "Code unique par type d’adhésion (ex: M001, V001, D001)"
#         ),
#     )

#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
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
#         verbose_name = _("Profil utilisateur")
#         verbose_name_plural = _("Profils utilisateur")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.full_name or str(self.user)

#     def save(self, *args, **kwargs):
#         """
#         Génère automatiquement le code d'inscription
#         basé sur le type d’adhésion.
#         """
#         if not self.registration_code and self.membership_role:
#             prefix_map = {
#                 "MEMBER": "M",
#                 "VOLUNTEER": "V",
#                 "SPONSOR": "D",
#                 "INSTITUTION": "I",
#             }

#             role_code = self.membership_role.code.upper()
#             prefix = prefix_map.get(role_code, "X")

#             count = (
#                 UserProfile.objects.filter(
#                     membership_role__code=self.membership_role.code
#                 ).count()
#                 + 1
#             )

#             self.registration_code = f"{prefix}{str(count).zfill(3)}"

#         super().save(*args, **kwargs)










# # accounts_users/models/users_profile.py ->01/07

# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from accounts_users.models.membership_role import MembershipRole


# class ValidationStatus(models.TextChoices):
#     PENDING = 'pending', _("En attente")
#     APPROVED = 'approved', _("Validé")
#     REJECTED = 'rejected', _("Refusé")


# class UserProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     full_name = models.CharField(_("Nom complet"), max_length=255)
#     phone = models.CharField(_("Téléphone"), max_length=30)
#     country = models.CharField(_("Pays"), max_length=100)
#     message = models.TextField(_("Message"), blank=True)

#     judicial_record = models.FileField(
#         _("Casier judiciaire"),
#         upload_to='judicial_records/',
#         blank=False,
#         null=False
#     )
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to='profile_pictures/',
#         blank=False,
#         null=False
#     )

#     role = models.ForeignKey(
#         MembershipRole,
#         verbose_name=_("Rôle"),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="userprofile_role"
#     )
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         verbose_name=_("Type d’adhésion"),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="userprofile_membership"
#     )

#     # ✅ Nouveau champ de statut avec enum
#     status = models.CharField(
#         _("Statut du profil"),
#         max_length=10,
#         choices=ValidationStatus.choices,
#         default=ValidationStatus.PENDING
#     )

#     created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Dernière modification"), auto_now=True)

#     def __str__(self):
#         return self.user.email




# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from accounts_users.models.membership_role import MembershipRole  # ✅ correction claire

# class UserProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=30)
#     country = models.CharField(max_length=100)
#     message = models.TextField(blank=True)
#     judicial_record = models.FileField(upload_to='judicial_records/', blank=False, null=False)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=False, null=False)

#     # ✅ Deux types de rôles différenciés
#     role = models.ForeignKey(
#         MembershipRole,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="userprofile_role"
#     )
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="userprofile_membership"
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.user.email







# # MODELE : accounts_users/models/users_profile.py
# from django.db import models
# from django.conf import settings
# from accounts_users.models.role import UserRole
# from accounts_users.models.membership_role import MembershipRole
# from django.utils.translation import gettext_lazy as _

# class UserProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=30)
#     country = models.CharField(max_length=100)
#     message = models.TextField(blank=True)
#     judicial_record = models.FileField(upload_to='judicial_records/', blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
#     role = models.ForeignKey(UserRole, null=True, blank=True, on_delete=models.SET_NULL, related_name="dashboard_user_profiles")
#     membership_role = models.ForeignKey(MembershipRole, null=True, blank=True, on_delete=models.SET_NULL, related_name="membership_profiles")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.user.email

