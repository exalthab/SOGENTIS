# accounts_users/models/role.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from django.conf import settings


# Admin-level roles
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Admin Role"
        verbose_name_plural = "Admin Roles"

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"



# # accounts_users/models/role.py -> 01/07
# from django.db import models
# from django.conf import settings
# from accounts_users.models.base import TimeStampedModel
# from django.utils.translation import gettext_lazy as _

# class UserRole(TimeStampedModel):
#     class RoleChoices(models.TextChoices):
#         SPONSOR = "SPONSOR", _("Sponsor")
#         VOLUNTEER = "VOLUNTEER", _("Volontaire")
#         MEMBER = "MEMBER", _("Membre")
#         DONOR = "DONOR", _("Donateur")
#         OTHER = "OTHER", _("Autre")

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="role_profile"
#     )
#     role = models.CharField(
#         max_length=20,
#         choices=RoleChoices.choices,
#         default=RoleChoices.MEMBER
#     )
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.user.email} – {self.get_role_display()}"
