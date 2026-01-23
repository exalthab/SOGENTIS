# accounts_users/models/economic/company_profile.py
from __future__ import annotations

import os
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel
from accounts_users.models.users_economic_profile import UserEconomicProfile


def company_document_upload(instance, filename: str) -> str:
    # nom de fichier stable (évite espaces bizarres)
    base, ext = os.path.splitext(filename or "")
    ext = (ext or ".pdf").lower()
    safe_base = "".join(c for c in (base or "document") if c.isalnum() or c in ("-", "_"))[:60] or "document"
    return f"companies/{instance.profile.user_id}/{safe_base}{ext}"


class CompanyProfile(TimeStampedModel):
    """
    Profil économique – Entreprise / Organisation (B2B)

    - Ne duplique pas l'identité de base (UserEconomicProfile)
    - Contient les attributs entreprise + pièces justificatives
    """

    profile = models.OneToOneField(
        UserEconomicProfile,
        on_delete=models.CASCADE,
        related_name="company_profile",
        verbose_name=_("Profil économique"),
    )

    company_name = models.CharField(_("Nom de la société"), max_length=255)
    owner_name = models.CharField(_("Nom du représentant légal"), max_length=255, blank=True, default="")
    company_address = models.TextField(_("Adresse de la société"), blank=True, default="")
    postal_code = models.CharField(_("Code postal"), max_length=20, blank=True, default="")

    registration_number = models.CharField(
        _("N° d’enregistrement / RCCM (optionnel)"),
        max_length=120,
        blank=True,
        default="",
        help_text=_("RCCM/registre ou identifiant officiel si disponible."),
    )

    registration_document = models.FileField(
        _("Document d’enregistrement légal (PDF)"),
        upload_to=company_document_upload,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        blank=True,
        null=True,
        help_text=_("PDF recommandé."),
    )

    financial_document = models.FileField(
        _("Document financier / Good standing (PDF)"),
        upload_to=company_document_upload,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        blank=True,
        null=True,
    )

    verified = models.BooleanField(_("Entreprise vérifiée"), default=False)
    verified_at = models.DateTimeField(_("Vérifiée le"), blank=True, null=True)
    verified_by = models.ForeignKey(
        "accounts_users.CustomUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verified_companies",
        verbose_name=_("Vérifiée par"),
        limit_choices_to={"is_staff": True},
    )

    class Meta:
        verbose_name = _("Profil entreprise")
        verbose_name_plural = _("Profils entreprises")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["verified"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return _("Entreprise – %(name)s") % {"name": self.company_name}

    def mark_verified(self, by_user=None):
        from django.utils import timezone
        self.verified = True
        self.verified_at = timezone.now()
        self.verified_by = by_user
        self.save(update_fields=["verified", "verified_at", "verified_by", "updated_at"])

    def mark_unverified(self, by_user=None, note: str = ""):
        # by_user/note réservés si tu ajoutes un audit plus tard
        self.verified = False
        self.verified_at = None
        self.verified_by = None
        self.save(update_fields=["verified", "verified_at", "verified_by", "updated_at"])






# # accounts_users/models/economic/company_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.users_economic_profile import UserEconomicProfile


# def company_document_upload(instance, filename):
#     return f"companies/{instance.profile.user.id}/{filename}"


# class CompanyProfile(TimeStampedModel):
#     """
#     Profil économique – Entreprise / Organisation B2B
#     """

#     profile = models.OneToOneField(
#         UserEconomicProfile,
#         on_delete=models.CASCADE,
#         related_name="company_profile",
#         verbose_name=_("Profil économique"),
#     )

#     company_name = models.CharField(_("Nom de la société"), max_length=255)
#     owner_name = models.CharField(_("Nom du représentant légal"), max_length=255)
#     company_address = models.TextField(_("Adresse de la société"))

#     postal_code = models.CharField(_("Code postal"), max_length=20, blank=True, null=True)

#     registration_document = models.FileField(
#         _("Document d’enregistrement légal"),
#         upload_to=company_document_upload,
#     )

#     financial_document = models.FileField(
#         _("Document financier / Good standing"),
#         upload_to=company_document_upload,
#         blank=True,
#         null=True,
#     )

#     verified = models.BooleanField(_("Entreprise vérifiée"), default=False)

#     class Meta:
#         verbose_name = _("Profil entreprise")
#         verbose_name_plural = _("Profils entreprises")

#     def __str__(self):
#         return _("Entreprise – %(name)s") % {"name": self.company_name}









# # accounts_users/models/economic/company_profile.py 30/12/2025
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.users_economic_profile import UserEconomicProfile


# def company_document_upload(instance, filename):
#     return f"companies/{instance.profile.user.id}/{filename}"


# class CompanyProfile(TimeStampedModel):
#     """
#     Profil économique – Entreprise / Organisation B2B
#     """

#     profile = models.OneToOneField(
#         UserEconomicProfile,
#         on_delete=models.CASCADE,
#         related_name="company_profile",
#         verbose_name=_("Profil économique"),
#     )

#     company_name = models.CharField(_("Nom de la société"), max_length=255)
#     owner_name = models.CharField(_("Nom du représentant légal"), max_length=255)
#     company_address = models.TextField(_("Adresse de la société"))

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#         null=True,
#     )

#     registration_document = models.FileField(
#         _("Document d’enregistrement légal"),
#         upload_to=company_document_upload,
#     )

#     financial_document = models.FileField(
#         _("Document financier / Good standing"),
#         upload_to=company_document_upload,
#         blank=True,
#         null=True,
#     )

#     verified = models.BooleanField(_("Entreprise vérifiée"), default=False)

#     class Meta:
#         verbose_name = _("Profil entreprise")
#         verbose_name_plural = _("Profils entreprises")

#     def __str__(self):
#         return _("Entreprise – %(name)s") % {"name": self.company_name}





# # accounts_users/models/economic/company_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_economic_profile import UserProfile


# def company_document_upload(instance, filename):
#     return f"companies/{instance.profile.user.id}/{filename}"


# class CompanyProfile(models.Model):
#     """
#     Profil économique – Entreprise / Organisation B2B
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="company_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     company_name = models.CharField(_("Nom de la société"), max_length=255)

#     owner_name = models.CharField(_("Nom du représentant légal"), max_length=255)

#     company_address = models.TextField(_("Adresse de la société"))

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#         null=True,
#     )

#     registration_document = models.FileField(
#         _("Document d’enregistrement légal"),
#         upload_to=company_document_upload,
#     )

#     financial_document = models.FileField(
#         _("Document financier / Good standing"),
#         upload_to=company_document_upload,
#         blank=True,
#         null=True,
#     )

#     verified = models.BooleanField(_("Entreprise vérifiée"), default=False)

#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Profil entreprise")
#         verbose_name_plural = _("Profils entreprises")

#     def __str__(self):
#         return f"Entreprise – {self.company_name}"











# # accounts_users/models/economic/company_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# def company_document_upload(instance, filename):
#     return f"companies/{instance.profile.user.id}/{filename}"


# class CompanyProfile(models.Model):
#     """
#     Profil économique – Entreprise / Organisation B2B
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="company_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     company_name = models.CharField(
#         _("Nom de la société"),
#         max_length=255,
#     )

#     owner_name = models.CharField(
#         _("Nom du représentant légal"),
#         max_length=255,
#     )

#     company_address = models.TextField(
#         _("Adresse de la société"),
#     )

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#         null=True,
#     )

#     registration_document = models.FileField(
#         _("Document d’enregistrement légal"),
#         upload_to=company_document_upload,
#     )

#     financial_document = models.FileField(
#         _("Document financier / Good standing"),
#         upload_to=company_document_upload,
#         blank=True,
#         null=True,
#     )

#     verified = models.BooleanField(
#         _("Entreprise vérifiée"),
#         default=False,
#     )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     class Meta:
#         verbose_name = _("Profil entreprise")
#         verbose_name_plural = _("Profils entreprises")

#     def __str__(self):
#         return f"Entreprise – {self.company_name}"







# # accounts_users/models/economic/company_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# def company_document_upload(instance, filename):
#     return f"companies/{instance.profile.user.id}/{filename}"


# class CompanyProfile(models.Model):
#     """
#     Profil économique – Entreprise / Organisation B2B
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="company_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     company_name = models.CharField(
#         _("Nom de la société"),
#         max_length=255,
#     )

#     owner_name = models.CharField(
#         _("Nom du représentant légal"),
#         max_length=255,
#     )

#     company_address = models.TextField(
#         _("Adresse de la société"),
#     )

#     registration_document = models.FileField(
#         _("Document d’enregistrement légal"),
#         upload_to=company_document_upload,
#     )

#     financial_document = models.FileField(
#         _("Document financier / Good standing"),
#         upload_to=company_document_upload,
#         blank=True,
#         null=True,
#     )

#     verified = models.BooleanField(
#         _("Entreprise vérifiée"),
#         default=False,
#     )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     class Meta:
#         verbose_name = _("Profil entreprise")
#         verbose_name_plural = _("Profils entreprises")

#     def __str__(self):
#         return f"Entreprise – {self.company_name}"





# # accounts_users/models/economic/company_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# def company_document_upload(instance, filename):
#     return f"companies/{instance.profile.user.id}/{filename}"


# class CompanyProfile(models.Model):
#     """
#     Profil économique – Entreprise / B2B
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="company_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     company_name = models.CharField(
#         _("Nom de la société"),
#         max_length=255,
#     )

#     owner_name = models.CharField(
#         _("Nom du représentant légal"),
#         max_length=255,
#     )

#     company_address = models.TextField(
#         _("Adresse de la société"),
#     )

#     registration_document = models.FileField(
#         _("Document d’enregistrement"),
#         upload_to=company_document_upload,
#     )

#     financial_document = models.FileField(
#         _("Document financier / Good standing"),
#         upload_to=company_document_upload,
#         blank=True,
#         null=True,
#     )

#     verified = models.BooleanField(
#         _("Entreprise vérifiée"),
#         default=False,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Profil entreprise")
#         verbose_name_plural = _("Profils entreprises")

#     def __str__(self):
#         return f"Entreprise – {self.company_name}"
