# accounts_users/models/economic/company_profile.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel
from accounts_users.models.users_economic_profile import UserEconomicProfile


def company_document_upload(instance, filename):
    return f"companies/{instance.profile.user.id}/{filename}"


class CompanyProfile(TimeStampedModel):
    """
    Profil économique – Entreprise / Organisation B2B
    """

    profile = models.OneToOneField(
        UserEconomicProfile,
        on_delete=models.CASCADE,
        related_name="company_profile",
        verbose_name=_("Profil économique"),
    )

    company_name = models.CharField(_("Nom de la société"), max_length=255)
    owner_name = models.CharField(_("Nom du représentant légal"), max_length=255)
    company_address = models.TextField(_("Adresse de la société"))

    postal_code = models.CharField(_("Code postal"), max_length=20, blank=True, null=True)

    registration_document = models.FileField(
        _("Document d’enregistrement légal"),
        upload_to=company_document_upload,
    )

    financial_document = models.FileField(
        _("Document financier / Good standing"),
        upload_to=company_document_upload,
        blank=True,
        null=True,
    )

    verified = models.BooleanField(_("Entreprise vérifiée"), default=False)

    class Meta:
        verbose_name = _("Profil entreprise")
        verbose_name_plural = _("Profils entreprises")

    def __str__(self):
        return _("Entreprise – %(name)s") % {"name": self.company_name}









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
