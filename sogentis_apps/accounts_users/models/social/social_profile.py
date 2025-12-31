# accounts_users/models/social/social_profile.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now

from accounts_users.models.membership_role import MembershipRole

# ======================================================
# UPLOAD PATHS
# ======================================================
def social_judicial_record_upload_path(instance, filename):
    return f"social/judicial_records/{instance.user.id}/{filename}"

def social_profile_picture_upload_path(instance, filename):
    return f"social/profile_pictures/{instance.user.id}/{filename}"

# ======================================================
# MODEL
# ======================================================
class SocialProfile(models.Model):
    """Profil SOCIAL (ONG) utilisateur."""

    # --------------------------------------------------
    # STATUT SOCIAL
    # --------------------------------------------------
    class Status(models.TextChoices):
        PENDING = "pending", _("En attente")
        APPROVED = "approved", _("Approuvé")
        REJECTED = "rejected", _("Refusé")

    # --------------------------------------------------
    # LIEN UTILISATEUR
    # --------------------------------------------------
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="social_profile",
        verbose_name=_("Utilisateur"),
    )

    # --------------------------------------------------
    # IDENTITÉ
    # --------------------------------------------------
    first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
    middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
    nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
    place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

    # --------------------------------------------------
    # RÉSIDENCE
    # --------------------------------------------------
    city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
    address = models.TextField(_("Adresse"), blank=True, null=True)
    country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
    country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

    # --------------------------------------------------
    # CONTACT / PROFESSION
    # --------------------------------------------------
    phone = PhoneNumberField(_("Téléphone"), region=None, max_length=30, blank=True, null=True)
    phone_verified = models.BooleanField(_("Téléphone vérifié"), default=False)
    phone_verified_at = models.DateTimeField(_("Téléphone vérifié le"), blank=True, null=True)

    profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
    function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

    # --------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------
    profile_picture = models.ImageField(
        _("Photo de profil"),
        upload_to=social_profile_picture_upload_path,
        blank=True,
        null=True,
    )
    judicial_record = models.FileField(
        _("Casier judiciaire (PDF)"),
        upload_to=social_judicial_record_upload_path,
        blank=True,
        null=True,
    )

    # --------------------------------------------------
    # ADHÉSION SOCIALE ONG
    # --------------------------------------------------
    membership_role = models.ForeignKey(
        MembershipRole,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Type d’adhésion sociale"),
    )
    membership_date = models.DateField(_("Date d’adhésion"), blank=True, null=True)
    is_active_member = models.BooleanField(_("Membre actif"), default=False)

    # --------------------------------------------------
    # ENGAGEMENT SOCIAL
    # --------------------------------------------------
    motivation = models.TextField(_("Motivation / Engagement social"), blank=True)
    availability = models.CharField(_("Disponibilité"), max_length=150, blank=True)
    skills = models.TextField(_("Compétences"), blank=True)

    # --------------------------------------------------
    # STATUT DE VALIDATION ONG
    # --------------------------------------------------
    status = models.CharField(_("Statut"), max_length=20, choices=Status.choices, default=Status.PENDING)
    is_validated = models.BooleanField(_("Validé"), default=False)
    validated_at = models.DateTimeField(_("Validé le"), blank=True, null=True)

    # --------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    # --------------------------------------------------
    # META
    # --------------------------------------------------
    class Meta:
        verbose_name = _("Profil social (ONG)")
        verbose_name_plural = _("Profils sociaux (ONG)")
        ordering = ["-created_at"]

    # --------------------------------------------------
    # STRING
    # --------------------------------------------------
    def __str__(self):
        return f"Profil social – {self.last_name or ''} {self.first_name or ''}".strip()

    # --------------------------------------------------
    # NORMALISATION PAYS
    # --------------------------------------------------
    def _normalize_country(self, value):
        if not value:
            return None
        if hasattr(value, "code"):
            return value.code.upper()
        if isinstance(value, str):
            value = value.strip().upper()
            if len(value) == 2:
                return value
        return None

    def clean(self):
        for field in ("country_of_birth", "country_of_residence"):
            value = getattr(self, field)
            if value and self._normalize_country(value) is None:
                raise ValidationError({
                    field: _("Pays invalide : code ISO alpha-2 requis.")
                })

    def save(self, *args, **kwargs):
        self.country_of_birth = self._normalize_country(self.country_of_birth)
        self.country_of_residence = self._normalize_country(self.country_of_residence)
        super().save(*args, **kwargs)

    # --------------------------------------------------
    # MÉTHODES UTILITAIRES
    # --------------------------------------------------
    def mark_phone_verified(self):
        """Marque le téléphone comme vérifié."""
        self.phone_verified = True
        self.phone_verified_at = now()
        self.save(update_fields=["phone_verified", "phone_verified_at"])




# # accounts_users/models/social/social_profile.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
# from django_countries.fields import CountryField
# from phonenumber_field.modelfields import PhoneNumberField
# from django.utils.timezone import now

# from accounts_users.models.membership_role import MembershipRole


# # ======================================================
# # UPLOAD PATHS
# # ======================================================
# def social_judicial_record_upload_path(instance, filename):
#     return f"social/judicial_records/{instance.user.id}/{filename}"


# def social_profile_picture_upload_path(instance, filename):
#     return f"social/profile_pictures/{instance.user.id}/{filename}"


# # ======================================================
# # MODEL
# # ======================================================
# class SocialProfile(models.Model):
#     """
#     Profil SOCIAL (ONG) utilisateur.
#     """

#     # --------------------------------------------------
#     # STATUT SOCIAL
#     # --------------------------------------------------
#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")

#     # --------------------------------------------------
#     # LIEN UTILISATEUR
#     # --------------------------------------------------
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name="social_profile",
#         verbose_name=_("Utilisateur"),
#     )

#     # --------------------------------------------------
#     # IDENTITÉ
#     # --------------------------------------------------
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres noms"), max_length=255, blank=True, null=True)
#     nickname = models.CharField(_("Surnom"), max_length=100, blank=True, null=True)
#     date_of_birth = models.DateField(_("Date de naissance"), blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=255, blank=True, null=True)

#     # --------------------------------------------------
#     # RÉSIDENCE
#     # --------------------------------------------------
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # --------------------------------------------------
#     # CONTACT / PROFESSION
#     # --------------------------------------------------
#     phone = PhoneNumberField(_("Téléphone"), region=None, max_length=30, blank=True, null=True)
#     phone_verified = models.BooleanField(_("Téléphone vérifié"), default=False)
#     phone_verified_at = models.DateTimeField(_("Téléphone vérifié le"), blank=True, null=True)

#     profession = models.CharField(_("Profession"), max_length=150, blank=True, null=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True, null=True)

#     # --------------------------------------------------
#     # DOCUMENTS
#     # --------------------------------------------------
#     profile_picture = models.ImageField(
#         _("Photo de profil"),
#         upload_to=social_profile_picture_upload_path,
#         blank=True,
#         null=True,
#     )
#     judicial_record = models.FileField(
#         _("Casier judiciaire (PDF)"),
#         upload_to=social_judicial_record_upload_path,
#         blank=True,
#         null=True,
#     )

#     # --------------------------------------------------
#     # ADHÉSION SOCIALE ONG
#     # --------------------------------------------------
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Type d’adhésion sociale"),
#     )
#     membership_date = models.DateField(_("Date d’adhésion"), blank=True, null=True)
#     is_active_member = models.BooleanField(_("Membre actif"), default=False)

#     # --------------------------------------------------
#     # ENGAGEMENT SOCIAL
#     # --------------------------------------------------
#     motivation = models.TextField(_("Motivation / Engagement social"), blank=True)
#     availability = models.CharField(_("Disponibilité"), max_length=150, blank=True)
#     skills = models.TextField(_("Compétences"), blank=True)

#     # --------------------------------------------------
#     # STATUT DE VALIDATION ONG
#     # --------------------------------------------------
#     status = models.CharField(_("Statut"), max_length=20, choices=Status.choices, default=Status.PENDING)
#     is_validated = models.BooleanField(_("Validé"), default=False)
#     validated_at = models.DateTimeField(_("Validé le"), blank=True, null=True)

#     # --------------------------------------------------
#     # TIMESTAMPS
#     # --------------------------------------------------
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     # --------------------------------------------------
#     # META
#     # --------------------------------------------------
#     class Meta:
#         verbose_name = _("Profil social (ONG)")
#         verbose_name_plural = _("Profils sociaux (ONG)")
#         ordering = ["-created_at"]

#     # --------------------------------------------------
#     # STRING
#     # --------------------------------------------------
#     def __str__(self):
#         return f"Profil social – {self.last_name or ''} {self.first_name or ''}".strip()

#     # --------------------------------------------------
#     # NORMALISATION PAYS
#     # --------------------------------------------------
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

#     def clean(self):
#         for field in ("country_of_birth", "country_of_residence"):
#             value = getattr(self, field)
#             if value and self._normalize_country(value) is None:
#                 raise ValidationError({
#                     field: _("Pays invalide : code ISO alpha-2 requis.")
#                 })

#     def save(self, *args, **kwargs):
#         self.country_of_birth = self._normalize_country(self.country_of_birth)
#         self.country_of_residence = self._normalize_country(self.country_of_residence)
#         super().save(*args, **kwargs)

#     # --------------------------------------------------
#     # MÉTHODES UTILITAIRES
#     # --------------------------------------------------
#     def mark_phone_verified(self):
#         self.phone_verified = True
#         self.phone_verified_at = now()
#         self.save(update_fields=["phone_verified", "phone_verified_at"])




# # accounts_users/models/social/social_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_countries.fields import CountryField
# from accounts_users.models.membership_role import MembershipRole
# from phonenumber_field.modelfields import PhoneNumberField
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class SocialProfile(models.Model):
#     """
#     Profil SOCIAL utilisateur.
#     - Combines identity, social engagement, and membership
#     """
#     # ======================================================
#     # STATUT
#     # ======================================================
#     class Status(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         APPROVED = "approved", _("Approuvé")
#         REJECTED = "rejected", _("Refusé")


#     # ==================================================
#     # LINK TO USER
#     # ==================================================
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="social_profile")

#     # ==================================================
#     # USER PROFILE — IDENTITÉ
#     # ==================================================
#     last_name = models.CharField(_("Nom"), max_length=150, blank=True, null=True)
#     first_name = models.CharField(_("Prénom"), max_length=150, blank=True, null=True)
#     middle_names = models.CharField(_("Autres prénoms"), max_length=150, blank=True)
#     nickname = models.CharField(_("Surnom"), max_length=150, blank=True)

#     # ==================================================
#     # NAISSANCE
#     # ==================================================
#     date_of_birth = models.DateField(_("Date de naissance"), max_length=255, blank=True, null=True)
#     place_of_birth = models.CharField(_("Lieu de naissance"), max_length=150)
#     country_of_birth = CountryField(_("Pays de naissance"), blank=True, null=True)

#     # ==================================================
#     # RÉSIDENCE
#     # ==================================================
#     country_of_residence = CountryField(_("Pays de résidence"), blank=True, null=True)
#     city_of_residence = models.CharField(_("Ville de résidence"), max_length=150, blank=True, null=True)
#     address = models.TextField(_("Adresse"), blank=True, null=True)

#     # ==================================================
#     # CONTACT / PRO
#     # ==================================================
#     # phone = models.CharField(_("Téléphone"), max_length=50)
#     phone = PhoneNumberField(_("Téléphone"), region=None, max_length=50,)
#     profession = models.CharField(_("Profession"), max_length=150, blank=True)
#     function = models.CharField(_("Fonction"), max_length=150, blank=True)

#     # ==================================================
#     # DOCUMENTS
#     # ==================================================
#     profile_picture = models.ImageField(_("Photo de profil"), upload_to="profiles/", blank=True, null=True)
#     judicial_record = models.FileField(_("Casier judiciaire (PDF)"), upload_to="judicial_records/", blank=False, null=False)

#     # ==================================================
#     # ADHÉSION SOCIALE
#     # ==================================================
#     membership_role = models.ForeignKey(MembershipRole, on_delete=models.SET_NULL, blank=True, null=True)
#     membership_date = models.DateField(blank=True, null=True)
#     is_active_member = models.BooleanField(default=False)

#     # ==================================================
#     # ENGAGEMENT SOCIAL
#     # ==================================================
#     motivation = models.TextField(_("Motivation / Engagement social"), blank=True)
#     availability = models.CharField(_("Disponibilité"), max_length=150, blank=True)
#     skills = models.TextField(_("Compétences"), blank=True)

#     # ==================================================
#     # STATUT SOCIAL
#     # ==================================================
#     is_validated = models.BooleanField(default=False)
#     validated_at = models.DateTimeField(blank=True, null=True)

#     # ==================================================
#     # TIMESTAMPS
#     # ==================================================
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Profil social")
#         verbose_name_plural = _("Profils sociaux")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"Profil social – {self.first_name} {self.last_name}"







# # accounts_users/models/social/social_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole


# class SocialProfile(models.Model):
#     """
#     Profil SOCIAL utilisateur.
#     - Extension du UserProfile
#     - Gère l’adhésion sociale et l’engagement
#     - Séparé du pôle économique
#     """

#     # ==================================================
#     # LIEN PROFIL CENTRAL
#     # ==================================================
#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="social_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     # ==================================================
#     # ADHÉSION SOCIALE
#     # ==================================================
#     membership_role = models.ForeignKey(
#         MembershipRole,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         verbose_name=_("Type d’adhésion sociale"),
#     )

#     membership_date = models.DateField(
#         _("Date d’adhésion"),
#         blank=True,
#         null=True,
#     )

#     is_active_member = models.BooleanField(
#         _("Membre actif"),
#         default=False,
#     )

#     # ==================================================
#     # ENGAGEMENT SOCIAL
#     # ==================================================
#     motivation = models.TextField(
#         _("Motivation / Engagement social"),
#         blank=True,
#     )

#     availability = models.CharField(
#         _("Disponibilité"),
#         max_length=150,
#         blank=True,
#         help_text=_("Ex : week-end, temps partiel, temps plein"),
#     )

#     skills = models.TextField(
#         _("Compétences"),
#         blank=True,
#         help_text=_("Compétences utiles pour les actions sociales"),
#     )

#     # ==================================================
#     # STATUT SOCIAL
#     # ==================================================
#     is_validated = models.BooleanField(
#         _("Profil social validé"),
#         default=False,
#     )

#     validated_at = models.DateTimeField(
#         _("Date de validation"),
#         blank=True,
#         null=True,
#     )

#     # ==================================================
#     # TIMESTAMPS
#     # ==================================================
#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     updated_at = models.DateTimeField(
#         _("Mis à jour le"),
#         auto_now=True,
#     )

#     # ==================================================
#     # META
#     # ==================================================
#     class Meta:
#         verbose_name = _("Profil social")
#         verbose_name_plural = _("Profils sociaux")
#         ordering = ["-created_at"]

#     # ==================================================
#     # STRING
#     # ==================================================
#     def __str__(self):
#         return f"Profil social – {self.profile}"
