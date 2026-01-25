# economic/ecommerce/models/vendor.py
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor",
        verbose_name=_("Utilisateur"),
    )

    company_name = models.CharField(
        max_length=255,
        verbose_name=_("Nom de l’entreprise"),
    )

    slug = models.SlugField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("Slug"),
    )

    # ✅ VENDORCODE (utilisé pour SKU : <VENDORCODE>-<CATCODE>-<NNNN>)
    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Code vendeur (VENDORCODE)"),
        validators=[
            RegexValidator(
                r"^[A-Z0-9]{3,8}$",
                _("Format invalide. Ex: SOG, DTH, AFR (3–8 caractères A-Z/0-9)."),
            )
        ],
        help_text=_("Code stable utilisé pour les SKU. Ex: SOG, DTH, AFR."),
    )

    # Coordonnées
    contact_email = models.EmailField(
        blank=True,
        verbose_name=_("Email de contact"),
    )

    phone = models.CharField(
        max_length=40,
        blank=True,
        verbose_name=_("Téléphone"),
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Adresse"),
    )

    # Statuts marketplace
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Actif"),
        help_text=_("Désactiver pour masquer le vendeur sans supprimer ses données."),
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Vérifié"),
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Vérifié le"),
        help_text=_("Renseigné automatiquement au premier passage à Vérifié."),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Vendeur")
        verbose_name_plural = _("Vendeurs")
        ordering = ["-is_verified", "-is_active", "company_name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_verified"]),
        ]

    def __str__(self) -> str:
        return f"{self.company_name} ({self.code})" if self.code else self.company_name

    # -------------------------
    # Normalisation & règles métier
    # -------------------------
    def clean(self):
        super().clean()

        if self.company_name:
            self.company_name = self.company_name.strip()

        if self.code:
            self.code = self.code.strip().upper() or None

        if self.contact_email:
            self.contact_email = self.contact_email.strip().lower()

        if self.phone:
            self.phone = " ".join(self.phone.strip().split())

        if not self.slug and self.company_name:
            self.slug = slugify(self.company_name)[:255]

        # ✅ cohérence: vendeur désactivé ne peut pas être "vérifié"
        if self.is_verified and not self.is_active:
            raise ValidationError({"is_verified": _("Un vendeur inactif ne peut pas être vérifié.")})

    def save(self, *args, **kwargs):
        # normalisation sécurité même hors admin
        if self.code:
            self.code = self.code.strip().upper() or None
        if self.contact_email:
            self.contact_email = self.contact_email.strip().lower()
        if self.phone:
            self.phone = " ".join(self.phone.strip().split())
        if not self.slug and self.company_name:
            self.slug = slugify(self.company_name)[:255]

        # timestamps vérification (propre)
        if self.is_verified and self.verified_at is None:
            self.verified_at = timezone.now()
        if not self.is_verified and self.verified_at is not None:
            # optionnel mais cohérent: si on décocher "verified"
            self.verified_at = None

        self.full_clean()
        super().save(*args, **kwargs)

    # -------------------------
    # Helpers
    # -------------------------
    def get_vendorcode(self) -> str:
        return (self.code or "").strip().upper()







# # economic/ecommerce/models/vendor.py
# from __future__ import annotations

# from django.conf import settings
# from django.core.validators import RegexValidator
# from django.db import models
# from django.utils import timezone
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _


# class Vendor(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="vendor",
#         verbose_name=_("Utilisateur"),
#     )

#     company_name = models.CharField(
#         max_length=255,
#         verbose_name=_("Nom de l’entreprise"),
#     )

#     slug = models.SlugField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Slug"),
#     )

#     # ✅ VENDORCODE (utilisé pour SKU : <VENDORCODE>-<CATCODE>-<NNNN>)
#     # nullable pour compatibilité legacy
#     code = models.CharField(
#         max_length=8,
#         unique=True,
#         null=True,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Code vendeur (VENDORCODE)"),
#         validators=[
#             RegexValidator(
#                 r"^[A-Z0-9]{3,8}$",
#                 _("Format invalide. Ex: SOG, DTH, AFR (3–8 caractères A-Z/0-9)."),
#             )
#         ],
#         help_text=_("Code stable utilisé pour les SKU. Ex: SOG, DTH, AFR."),
#     )

#     # Coordonnées
#     contact_email = models.EmailField(
#         blank=True,
#         verbose_name=_("Email de contact"),
#     )

#     phone = models.CharField(
#         max_length=40,
#         blank=True,
#         verbose_name=_("Téléphone"),
#     )

#     address = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Adresse"),
#     )

#     # Statuts marketplace
#     is_active = models.BooleanField(
#         default=True,
#         db_index=True,
#         verbose_name=_("Actif"),
#         help_text=_("Désactiver pour masquer le vendeur sans supprimer ses données."),
#     )

#     is_verified = models.BooleanField(
#         default=False,
#         verbose_name=_("Vérifié"),
#     )

#     verified_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Vérifié le"),
#         help_text=_("Renseigné automatiquement au premier passage à Vérifié."),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Vendeur")
#         verbose_name_plural = _("Vendeurs")
#         ordering = ["company_name"]
#         indexes = [
#             models.Index(fields=["code"]),
#             models.Index(fields=["is_active", "is_verified"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.company_name} ({self.code})" if self.code else self.company_name

#     # -------------------------
#     # Validations & normalisation
#     # -------------------------
#     def clean(self):
#         super().clean()

#         if self.company_name:
#             self.company_name = self.company_name.strip()

#         if self.code:
#             self.code = self.code.strip().upper() or None

#         # slug auto si vide
#         if not self.slug and self.company_name:
#             self.slug = slugify(self.company_name)[:255]

#     def save(self, *args, **kwargs):
#         # Normalisation de sécurité (hors admin aussi)
#         if self.code:
#             self.code = self.code.strip().upper() or None

#         # Timestamp de vérification (une seule fois)
#         if self.is_verified and self.verified_at is None:
#             self.verified_at = timezone.now()

#         super().save(*args, **kwargs)

#     # -------------------------
#     # Helpers
#     # -------------------------
#     def get_vendorcode(self) -> str:
#         """Retourne le VENDORCODE normalisé (toujours MAJ)."""
#         return (self.code or "").strip().upper()






# # /economic/ecommerce/models/vendor.py

# from __future__ import annotations

# from django.conf import settings
# from django.core.validators import RegexValidator
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# class Vendor(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="vendor",  # 🔑 simple, unique, sans clash
#         verbose_name=_("Utilisateur"),
#     )

#     company_name = models.CharField(
#         max_length=255,
#         verbose_name=_("Nom de l’entreprise"),
#     )

#     # ✅ VENDORCODE (utile pour SKU : <VENDORCODE>-<CATCODE>-<NNNN>)
#     # nullable/blank pour ne pas casser les données existantes.
#     code = models.CharField(
#         max_length=8,
#         unique=True,
#         null=True,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Code vendeur (VENDORCODE)"),
#         validators=[
#             RegexValidator(
#                 r"^[A-Z0-9]{3,8}$",
#                 _("Format invalide. Ex: SOG, DTH, AFR (3–8 caractères A-Z/0-9)."),
#             )
#         ],
#         help_text=_("Code stable pour SKU. Ex: SOG, DTH, AFR..."),
#     )

#     # ✅ Coordonnées (utile en prod : factures, contact, SAV)
#     phone = models.CharField(
#         max_length=40,
#         blank=True,
#         verbose_name=_("Téléphone"),
#     )
#     email = models.EmailField(
#         blank=True,
#         verbose_name=_("Email"),
#     )
#     address = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Adresse"),
#     )

#     # ✅ Marketplace statuses
#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#         help_text=_("Désactiver pour cacher le vendeur sans supprimer ses données."),
#     )

#     is_verified = models.BooleanField(
#         default=False,
#         verbose_name=_("Vérifié"),
#     )

#     verified_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Vérifié le"),
#         help_text=_("Renseigné automatiquement au premier passage à Vérifié."),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Vendeur")
#         verbose_name_plural = _("Vendeurs")
#         ordering = ["company_name"]
#         indexes = [
#             models.Index(fields=["is_active", "is_verified"]),
#             models.Index(fields=["code"]),
#         ]

#     def __str__(self):
#         return f"{self.company_name} ({self.code})" if self.code else self.company_name

#     def clean(self):
#         super().clean()
#         # Normalise le code
#         if self.code:
#             self.code = self.code.strip().upper() or None

#     def save(self, *args, **kwargs):
#         # Normalise code avant save (sécurité en dehors de l'admin aussi)
#         if self.code:
#             self.code = self.code.strip().upper() or None

#         # Timestamp de vérification (au premier passage à True)
#         if self.is_verified and self.verified_at is None:
#             self.verified_at = timezone.now()

#         super().save(*args, **kwargs)

#     def get_vendorcode(self) -> str:
#         """Retourne VENDORCODE normalisé (toujours MAJ)."""
#         return (self.code or "").strip().upper()





# # /economic/ecommerce/models/vendor.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Vendor(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="vendor",          # 🔑 simple, unique, sans clash
#         verbose_name=_("Utilisateur"),
#     )

#     company_name = models.CharField(
#         max_length=255,
#         verbose_name=_("Nom de l’entreprise"),
#     )

#     is_verified = models.BooleanField(
#         default=False,
#         verbose_name=_("Vérifié"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     class Meta:
#         verbose_name = _("Vendeur")
#         verbose_name_plural = _("Vendeurs")

#     def __str__(self):
#         return self.company_name
