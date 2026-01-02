# economic/b2b/models/company.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    class CompanyStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        PENDING = "PENDING", _("En attente")
        SUSPENDED = "SUSPENDED", _("Suspendue")

    # 🔗 Propriétaire (indispensable en prod pour la sécurité & le filtrage)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="b2b_companies",
        verbose_name=_("Propriétaire"),
        null=True,   # ✅ pour migration douce si tu as déjà des lignes
        blank=True,
    )

    # 🏢 Identité
    name = models.CharField(_("Nom"), max_length=255)
    email = models.EmailField(_("Email"), blank=True)  # ✅ pas obligatoire (prod-friendly)
    phone = models.CharField(_("Téléphone"), max_length=50, blank=True)
    country = models.CharField(_("Pays"), max_length=2, blank=True)  # ISO2 (SN, FR…)
    city = models.CharField(_("Ville"), max_length=120, blank=True)
    address = models.CharField(_("Adresse"), max_length=255, blank=True)
    website = models.URLField(_("Site web"), blank=True)

    # ✅ compatible avec ton ancien champ
    is_active = models.BooleanField(_("Actif"), default=True)

    # ✅ status “métier” (évite d’utiliser is_active pour tout)
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=CompanyStatus.choices,
        default=CompanyStatus.ACTIVE,
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Entreprise")
        verbose_name_plural = _("Entreprises")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return self.name




# # economic/b2b/models/company.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# class Company(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["name"]
#         verbose_name = _("Entreprise")
#         verbose_name_plural = _("Entreprises")

#     def __str__(self):
#         return self.name
