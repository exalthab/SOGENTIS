# accounts_users/models/users_profile.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from accounts_users.models.membership_role import MembershipRole
from accounts_users.models.user_role import UserRole

# Ajout pour la gestion des pays
from django_countries.fields import CountryField

def judicial_record_upload_path(instance, filename):
    return f"users/judicial_records/{instance.user.id}/{filename}"

def profile_picture_upload_path(instance, filename):
    return f"users/profile_pictures/{instance.user.id}/{filename}"

class UserProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _("En attente")
        APPROVED = 'approved', _("Approuvé")
        REJECTED = 'rejected', _("Refusé")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userprofile",
        verbose_name=_("Utilisateur")
    )

    full_name = models.CharField(_("Nom complet"), max_length=255)
    phone = models.CharField(_("Téléphone"), max_length=30)
    # Remplace le CharField par le CountryField
    country = CountryField(verbose_name=_("Pays"))
    message = models.TextField(_("Message"), blank=True)

    profile_picture = models.ImageField(
        _("Photo de profil"),
        upload_to=profile_picture_upload_path,
        blank=True, null=True
    )
    judicial_record = models.FileField(
        _("Casier judiciaire"),
        upload_to=judicial_record_upload_path,
        blank=True, null=True
    )

    role = models.ForeignKey(
        UserRole,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("Rôle administratif")
    )
    membership_role = models.ForeignKey(
        MembershipRole,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("Type d’adhésion")
    )

    registration_code = models.CharField(
        _("Code d'inscription"),
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Code unique par type d’adhésion (ex: M001, V001, D001)")
    )

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Profil utilisateur")
        verbose_name_plural = _("Profils utilisateur")
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name or str(self.user)

    def save(self, *args, **kwargs):
        if not self.registration_code and self.membership_role:
            prefix_map = {
                'MEMBER': 'M',
                'VOLUNTEER': 'V',
                'SPONSOR': 'D',
                'INSTITUTION': 'I',
            }
            prefix = prefix_map.get(self.membership_role.code.upper(), 'X')
            existing = UserProfile.objects.filter(
                membership_role__code=self.membership_role.code
            ).count() + 1
            self.registration_code = f"{prefix}{str(existing).zfill(3)}"
        super().save(*args, **kwargs)












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

