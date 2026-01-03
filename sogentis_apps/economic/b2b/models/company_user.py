# economic/b2b/models/company_user.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CompanyUser(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrateur")
        STAFF = "staff", _("Employé")
        VIEWER = "viewer", _("Consultation")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_memberships",
        verbose_name=_("Utilisateur"),
    )

    company = models.ForeignKey(
        "b2b.Company",
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("Entreprise"),
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        verbose_name=_("Rôle"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Utilisateur entreprise")
        verbose_name_plural = _("Utilisateurs entreprise")
        constraints = [
            models.UniqueConstraint(fields=["user", "company"], name="unique_user_per_company"),
        ]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["user"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    def __str__(self) -> str:
        return f"{self.user} ({self.company})"






# # economic/b2b/models/company_user.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from .company import Company


# class CompanyUser(models.Model):
#     ROLE_CHOICES = [
#         ("admin", _("Administrateur")),
#         ("staff", _("Employé")),
#         ("viewer", _("Consultation")),
#     ]

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="company_memberships",
#         verbose_name=_("Utilisateur"),
#     )

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name="users",
#         verbose_name=_("Entreprise"),
#     )

#     role = models.CharField(
#         max_length=20,
#         choices=ROLE_CHOICES,
#         default="viewer",
#         verbose_name=_("Rôle"),
#     )

#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Utilisateur entreprise")
#         verbose_name_plural = _("Utilisateurs entreprise")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["user", "company"],
#                 name="unique_user_per_company",
#             )
#         ]
#         indexes = [
#             models.Index(fields=["company"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["role"]),
#             models.Index(fields=["is_active"]),
#         ]

#     @property
#     def is_admin(self):
#         return self.role == "admin"

#     def __str__(self):
#         return f"{self.user} ({self.company})"






# # /economic/b2b/models/company_user.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from .company import Company


# class CompanyUser(models.Model):
    
#     ROLE_CHOICES = [
#         ("admin", _("Administrateur")),
#         ("staff", _("Employé")),
#         ("viewer", _("Consultation")),
#     ]

#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="company_user",
#     )
#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name="users",
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def is_admin(self):
#         return self.role == "admin"

#     def __str__(self):
#         return f"{self.user} ({self.company})"
    
#     class Meta:
#         verbose_name = _("Utilisateur entreprise")
#         verbose_name_plural = _("Utilisateurs entreprise")
