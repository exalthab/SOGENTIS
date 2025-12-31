# accounts_users/models/economic/vendor_profile.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel
from accounts_users.models.users_economic_profile import UserEconomicProfile


def vendor_document_upload(instance, filename):
    return f"vendors/{instance.profile.user.id}/{filename}"


class VendorProfile(TimeStampedModel):
    """
    Profil économique – Vendeur / Commerçant
    """

    profile = models.OneToOneField(
        UserEconomicProfile,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
        verbose_name=_("Profil économique"),
    )

    business_name = models.CharField(_("Nom commercial"), max_length=255)

    ninea = models.CharField(
        _("NINEA / Identifiant commercial"),
        max_length=100,
        unique=True,
    )

    business_address = models.TextField(_("Adresse de l’activité"))

    postal_code = models.CharField(_("Code postal"), max_length=20, blank=True, null=True)

    trade_register_document = models.FileField(
        _("Registre de commerce / document légal"),
        upload_to=vendor_document_upload,
    )

    verified = models.BooleanField(_("Vendeur vérifié"), default=False)

    class Meta:
        verbose_name = _("Profil vendeur")
        verbose_name_plural = _("Profils vendeurs")

    def __str__(self):
        return _("Vendeur – %(name)s") % {"name": self.business_name}








# # accounts_users/models/economic/vendor_profile.py 25/12/2025
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.base import TimeStampedModel
# from accounts_users.models.users_economic_profile import UserEconomicProfile


# def vendor_document_upload(instance, filename):
#     return f"vendors/{instance.profile.user.id}/{filename}"


# class VendorProfile(TimeStampedModel):
#     """
#     Profil économique – Vendeur / Commerçant
#     """

#     profile = models.OneToOneField(
#         UserEconomicProfile,
#         on_delete=models.CASCADE,
#         related_name="vendor_profile",
#         verbose_name=_("Profil économique"),
#     )

#     business_name = models.CharField(_("Nom commercial"), max_length=255)

#     ninea = models.CharField(
#         _("NINEA / Identifiant commercial"),
#         max_length=100,
#         unique=True,
#     )

#     business_address = models.TextField(_("Adresse de l’activité"))

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#         null=True,
#     )

#     trade_register_document = models.FileField(
#         _("Registre de commerce / document légal"),
#         upload_to=vendor_document_upload,
#     )

#     verified = models.BooleanField(_("Vendeur vérifié"), default=False)

#     class Meta:
#         verbose_name = _("Profil vendeur")
#         verbose_name_plural = _("Profils vendeurs")

#     def __str__(self):
#         return _("Vendeur – %(name)s") % {"name": self.business_name}





# # accounts_users/models/economic/company_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_economic_profile import UserProfile


# def vendor_document_upload(instance, filename):
#     return f"vendors/{instance.profile.user.id}/{filename}"


# class VendorProfile(models.Model):
#     """
#     Profil économique – Vendeur / Commerçant
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="vendor_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     business_name = models.CharField(_("Nom commercial"), max_length=255)

#     ninea = models.CharField(
#         _("NINEA / Identifiant commercial"),
#         max_length=100,
#         unique=True,
#     )

#     business_address = models.TextField(_("Adresse de l’activité"))

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#         null=True,
#     )

#     trade_register_document = models.FileField(
#         _("Registre de commerce / document légal"),
#         upload_to=vendor_document_upload,
#     )

#     verified = models.BooleanField(_("Vendeur vérifié"), default=False)

#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Profil vendeur")
#         verbose_name_plural = _("Profils vendeurs")

#     def __str__(self):
#         return f"Vendeur – {self.business_name}"







# # accounts_users/models/economic/vendor_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# def vendor_document_upload(instance, filename):
#     return f"vendors/{instance.profile.user.id}/{filename}"


# class VendorProfile(models.Model):
#     """
#     Profil économique – Vendeur / Commerçant
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="vendor_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     business_name = models.CharField(_("Nom commercial"), max_length=255)

#     ninea = models.CharField(
#         _("NINEA / Identifiant commercial"),
#         max_length=100,
#         unique=True,
#     )

#     business_address = models.TextField(_("Adresse de l’activité"))

#     postal_code = models.CharField(
#         _("Code postal"),
#         max_length=20,
#         blank=True,
#         null=True,
#     )

#     trade_register_document = models.FileField(
#         _("Registre de commerce / document légal"),
#         upload_to=vendor_document_upload,
#     )

#     verified = models.BooleanField(_("Vendeur vérifié"), default=False)

#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Profil vendeur")
#         verbose_name_plural = _("Profils vendeurs")

#     def __str__(self):
#         return f"Vendeur – {self.business_name}"






# # accounts_users/models/economic/vendor_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# def vendor_document_upload(instance, filename):
#     return f"vendors/{instance.profile.user.id}/{filename}"


# class VendorProfile(models.Model):
#     """
#     Profil économique – Vendeur / Commerçant
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="vendor_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     business_name = models.CharField(
#         _("Nom commercial"),
#         max_length=255,
#     )

#     ninea = models.CharField(
#         _("NINEA / Identifiant commercial"),
#         max_length=100,
#         unique=True,
#     )

#     business_address = models.TextField(
#         _("Adresse de l’activité"),
#     )

#     trade_register_document = models.FileField(
#         _("Registre de commerce / document légal"),
#         upload_to=vendor_document_upload,
#     )

#     verified = models.BooleanField(
#         _("Vendeur vérifié"),
#         default=False,
#     )

#     created_at = models.DateTimeField(
#         _("Créé le"),
#         auto_now_add=True,
#     )

#     class Meta:
#         verbose_name = _("Profil vendeur")
#         verbose_name_plural = _("Profils vendeurs")

#     def __str__(self):
#         return f"Vendeur – {self.business_name}"





# # accounts_users/models/economic/vendor_profile.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# def vendor_document_upload(instance, filename):
#     return f"vendors/{instance.profile.user.id}/{filename}"


# class VendorProfile(models.Model):
#     """
#     Profil économique – Vendeur
#     """

#     profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         related_name="vendor_profile",
#         verbose_name=_("Profil utilisateur"),
#     )

#     business_name = models.CharField(
#         _("Nom commercial"),
#         max_length=255,
#     )

#     ninea = models.CharField(
#         _("NINEA / Identifiant commercial"),
#         max_length=100,
#         unique=True,
#     )

#     business_address = models.TextField(
#         _("Adresse de l’activité"),
#     )

#     trade_register_document = models.FileField(
#         _("Registre de commerce"),
#         upload_to=vendor_document_upload,
#         # upload_to="vendors/trade_registers/",

#     )

#     verified = models.BooleanField(
#         _("Vendeur vérifié"),
#         default=False,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Profil vendeur")
#         verbose_name_plural = _("Profils vendeurs")

#     def __str__(self):
#         return f"Vendeur – {self.business_name}"
