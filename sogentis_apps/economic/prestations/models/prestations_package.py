# economic/prestations/models/prestations_package.py
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field
from parler.models import TranslatableModel, TranslatedFields

from .prestations import Prestation


class PrestationPackage(TranslatableModel):
    """
    Pack de prestations – version PRODUCTION AVANCÉE.
    """

    # ==================================================
    # ENUMS MÉTIER
    # ==================================================
    class BillingPeriod(models.TextChoices):
        YEARLY = "yearly", _("Annuel")
        MONTHLY = "monthly", _("Mensuel")
        ONE_TIME = "one_time", _("Ponctuel")
        CUSTOM = "custom", _("Sur devis")

    class Tier(models.TextChoices):
        STARTER = "starter", _("Starter")
        BUSINESS = "business", _("Business")
        PREMIUM = "premium", _("Premium")
        ENTERPRISE = "enterprise", _("Enterprise")
        CUSTOM = "custom", _("Sur mesure")

    class SupportLevel(models.TextChoices):
        STANDARD = "standard", _("Standard")
        PRIORITY = "priority", _("Prioritaire")
        DEDICATED = "dedicated", _("Dédié")

    class Currency(models.TextChoices):
        EUR = "EUR", "EUR"
        XOF = "XOF", "XOF"
        USD = "USD", "USD"

    # ==================================================
    # TRADUCTIONS / MARKETING / SEO
    # ==================================================
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name=_("Nom du pack")),
        description=CKEditor5Field(blank=True, verbose_name=_("Description détaillée")),
        tagline=models.CharField(
            max_length=220,
            blank=True,
            verbose_name=_("Accroche marketing"),
            help_text=_("Phrase courte orientée valeur"),
        ),
        cta_label=models.CharField(
            max_length=40,
            blank=True,
            default=_("Demander un devis"),
            verbose_name=_("Libellé du bouton (CTA)"),
        ),
        seo_title=models.CharField(max_length=70, blank=True, verbose_name=_("SEO title")),
        seo_description=models.CharField(max_length=160, blank=True, verbose_name=_("SEO description")),
    )

    # ==================================================
    # IDENTITÉ & RELATIONS
    # ==================================================
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

    prestations = models.ManyToManyField(
        Prestation,
        related_name="packages",
        blank=True,
        verbose_name=_("Prestations incluses"),
    )

    # ==================================================
    # PRICING & OFFRE COMMERCIALE
    # ==================================================
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Prix total"),
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.EUR,
        verbose_name=_("Devise"),
    )

    billing_period = models.CharField(
        max_length=16,
        choices=BillingPeriod.choices,
        default=BillingPeriod.YEARLY,
        verbose_name=_("Périodicité"),
    )

    tier = models.CharField(
        max_length=16,
        choices=Tier.choices,
        default=Tier.STARTER,
        verbose_name=_("Niveau de pack"),
    )

    support_level = models.CharField(
        max_length=16,
        choices=SupportLevel.choices,
        default=SupportLevel.STANDARD,
        verbose_name=_("Niveau de support"),
    )

    # ==================================================
    # OPTIONS / LIMITES
    # ==================================================
    included_domain_year = models.BooleanField(default=False, verbose_name=_("Nom de domaine inclus (1 an)"))
    included_ssl = models.BooleanField(default=True, verbose_name=_("Certificat SSL inclus"))
    emails_count = models.PositiveIntegerField(default=0, verbose_name=_("Comptes e-mail professionnels"))

    max_pages = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Nombre maximal de pages"),
        help_text=_("Laisser vide si non applicable / illimité"),
    )

    # ==================================================
    # VISIBILITÉ / TRI / STATUT
    # ==================================================
    order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre d’affichage"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Publié le"))
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    # ==================================================
    # META
    # ==================================================
    class Meta:
        verbose_name = _("Pack de prestations")
        verbose_name_plural = _("Packs de prestations")
        ordering = ["-is_featured", "order", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_featured", "order"]),
            models.Index(fields=["tier", "billing_period", "currency"]),
        ]

    # ==================================================
    # CORE METHODS
    # ==================================================
    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or f"Pack #{self.pk}"

    def _base_slug_source(self) -> str:
        return (self.safe_translation_getter("name", any_language=True) or "").strip()

    def _ensure_unique_slug(self) -> None:
        if self.slug:
            return
        base = slugify(self._base_slug_source()) or "pack"
        slug = base
        i = 2
        Model = self.__class__
        while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{i}"
            i += 1
        self.slug = slug

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            super().save(*args, **kwargs)

        self._ensure_unique_slug()

        if self.is_active and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    # ==================================================
    # HELPERS
    # ==================================================
    def get_seo_title(self) -> str:
        return (
            self.safe_translation_getter("seo_title", any_language=True)
            or self.safe_translation_getter("name", any_language=True)
            or ""
        )

    def get_seo_description(self) -> str:
        return (
            self.safe_translation_getter("seo_description", any_language=True)
            or self.safe_translation_getter("tagline", any_language=True)
            or ""
        )

    def is_custom_pricing(self) -> bool:
        return self.billing_period == self.BillingPeriod.CUSTOM

    def formatted_price(self) -> str:
        if self.is_custom_pricing():
            return _("Sur devis")
        return f"{self.total_price:g} {self.currency}"


class PrestationPackageFeature(models.Model):
    package = models.ForeignKey(
        PrestationPackage,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("Pack"),
    )

    label = models.CharField(max_length=220, verbose_name=_("Élément"))

    is_highlight = models.BooleanField(
        default=False,
        verbose_name=_("Mettre en évidence"),
        help_text=_("Feature clé du pack"),
    )

    order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre"))

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Pack — Feature")
        verbose_name_plural = _("Pack — Features")
        indexes = [
            models.Index(fields=["package", "order"]),
        ]

    def __str__(self) -> str:
        return self.label






# # economic/prestations/models/prestations_package.py
# from __future__ import annotations

# from decimal import Decimal

# from django.db import models
# from django.utils import timezone
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _

# from django_ckeditor_5.fields import CKEditor5Field
# from parler.models import TranslatableModel, TranslatedFields

# from .prestations import Service


# class ServicePackage(TranslatableModel):
#     """
#     Pack de services – version PRODUCTION AVANCÉE.

#     ✔ Translatable (Parler)
#     ✔ SEO & marketing ready
#     ✔ Pricing structuré (tier, billing, currency)
#     ✔ Compatible devis / abonnement / one-shot
#     ✔ UX front & admin optimisés
#     ✔ Évolutif (options, upsell, bundles)
#     """

#     # ==================================================
#     # ENUMS MÉTIER
#     # ==================================================
#     class BillingPeriod(models.TextChoices):
#         YEARLY = "yearly", _("Annuel")
#         MONTHLY = "monthly", _("Mensuel")
#         ONE_TIME = "one_time", _("Ponctuel")
#         CUSTOM = "custom", _("Sur devis")

#     class Tier(models.TextChoices):
#         STARTER = "starter", _("Starter")
#         BUSINESS = "business", _("Business")
#         PREMIUM = "premium", _("Premium")
#         ENTERPRISE = "enterprise", _("Enterprise")
#         CUSTOM = "custom", _("Sur mesure")

#     class SupportLevel(models.TextChoices):
#         STANDARD = "standard", _("Standard")
#         PRIORITY = "priority", _("Prioritaire")
#         DEDICATED = "dedicated", _("Dédié")

#     class Currency(models.TextChoices):
#         EUR = "EUR", "EUR"
#         XOF = "XOF", "XOF"
#         USD = "USD", "USD"

#     # ==================================================
#     # TRADUCTIONS / MARKETING / SEO
#     # ==================================================
#     translations = TranslatedFields(
#         name=models.CharField(max_length=200, verbose_name=_("Nom du pack")),
#         description=CKEditor5Field(blank=True, verbose_name=_("Description détaillée")),

#         tagline=models.CharField(
#             max_length=220,
#             blank=True,
#             verbose_name=_("Accroche marketing"),
#             help_text=_("Phrase courte orientée valeur"),
#         ),

#         cta_label=models.CharField(
#             max_length=40,
#             blank=True,
#             default=_("Demander un devis"),
#             verbose_name=_("Libellé du bouton (CTA)"),
#         ),

#         seo_title=models.CharField(
#             max_length=70,
#             blank=True,
#             verbose_name=_("SEO title"),
#         ),
#         seo_description=models.CharField(
#             max_length=160,
#             blank=True,
#             verbose_name=_("SEO description"),
#         ),
#     )

#     # ==================================================
#     # IDENTITÉ & RELATIONS
#     # ==================================================
#     slug = models.SlugField(
#         unique=True,
#         blank=True,
#         null=True,
#         verbose_name=_("Slug"),
#     )

#     services = models.ManyToManyField(
#         Service,
#         related_name="packages",
#         blank=True,
#         verbose_name=_("Services inclus"),
#     )

#     # ==================================================
#     # PRICING & OFFRE COMMERCIALE
#     # ==================================================
#     total_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Prix total"),
#     )

#     currency = models.CharField(
#         max_length=3,
#         choices=Currency.choices,
#         default=Currency.EUR,
#         verbose_name=_("Devise"),
#     )

#     billing_period = models.CharField(
#         max_length=16,
#         choices=BillingPeriod.choices,
#         default=BillingPeriod.YEARLY,
#         verbose_name=_("Périodicité"),
#     )

#     tier = models.CharField(
#         max_length=16,
#         choices=Tier.choices,
#         default=Tier.STARTER,
#         verbose_name=_("Niveau de pack"),
#     )

#     support_level = models.CharField(
#         max_length=16,
#         choices=SupportLevel.choices,
#         default=SupportLevel.STANDARD,
#         verbose_name=_("Niveau de support"),
#     )

#     # ==================================================
#     # OPTIONS / LIMITES (OFFRE STRUCTURÉE)
#     # ==================================================
#     included_domain_year = models.BooleanField(
#         default=False,
#         verbose_name=_("Nom de domaine inclus (1 an)"),
#     )

#     included_ssl = models.BooleanField(
#         default=True,
#         verbose_name=_("Certificat SSL inclus"),
#     )

#     emails_count = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Comptes e-mail professionnels"),
#     )

#     max_pages = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         verbose_name=_("Nombre maximal de pages"),
#         help_text=_("Laisser vide si non applicable / illimité"),
#     )

#     # ==================================================
#     # VISIBILITÉ / TRI / STATUT
#     # ==================================================
#     order = models.PositiveIntegerField(
#         default=100,
#         verbose_name=_("Ordre d’affichage"),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mis en avant"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     published_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Publié le"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         editable=False,
#         verbose_name=_("Créé le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     # ==================================================
#     # META
#     # ==================================================
#     class Meta:
#         verbose_name = _("Pack de services")
#         verbose_name_plural = _("Packs de services")
#         ordering = ["-is_featured", "order", "-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["slug"]),
#             models.Index(fields=["is_active", "is_featured", "order"]),
#             models.Index(fields=["tier", "billing_period", "currency"]),
#         ]

#     # ==================================================
#     # CORE METHODS
#     # ==================================================
#     def __str__(self) -> str:
#         return self.safe_translation_getter("name", any_language=True) or f"Pack #{self.pk}"

#     def _base_slug_source(self) -> str:
#         return (self.safe_translation_getter("name", any_language=True) or "").strip()

#     def _ensure_unique_slug(self):
#         if self.slug:
#             return

#         base = slugify(self._base_slug_source()) or "pack"
#         slug = base
#         i = 2
#         Model = self.__class__

#         while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#             slug = f"{base}-{i}"
#             i += 1

#         self.slug = slug

#     def save(self, *args, **kwargs):
#         # Double save initial pour slug unique fiable
#         if not self.pk and not self.slug:
#             super().save(*args, **kwargs)

#         self._ensure_unique_slug()

#         # Publication auto si actif
#         if self.is_active and not self.published_at:
#             self.published_at = timezone.now()

#         super().save(*args, **kwargs)

#     # ==================================================
#     # HELPERS BUSINESS / SEO
#     # ==================================================
#     def get_seo_title(self) -> str:
#         return (
#             self.safe_translation_getter("seo_title", any_language=True)
#             or self.safe_translation_getter("name", any_language=True)
#             or ""
#         )

#     def get_seo_description(self) -> str:
#         return (
#             self.safe_translation_getter("seo_description", any_language=True)
#             or self.safe_translation_getter("tagline", any_language=True)
#             or ""
#         )

#     def is_custom_pricing(self) -> bool:
#         return self.billing_period == self.BillingPeriod.CUSTOM

#     def formatted_price(self) -> str:
#         if self.is_custom_pricing():
#             return _("Sur devis")
#         return f"{self.total_price:g} {self.currency}"


# class ServicePackageFeature(models.Model):
#     """
#     Bullet points / avantages d’un pack (admin-driven).
#     Utilisé pour pages pricing, comparatifs, landing pages.
#     """

#     package = models.ForeignKey(
#         ServicePackage,
#         on_delete=models.CASCADE,
#         related_name="features",
#     )

#     label = models.CharField(
#         max_length=220,
#         verbose_name=_("Élément"),
#     )

#     is_highlight = models.BooleanField(
#         default=False,
#         verbose_name=_("Mettre en évidence"),
#         help_text=_("Feature clé du pack"),
#     )

#     order = models.PositiveIntegerField(
#         default=100,
#         verbose_name=_("Ordre"),
#     )

#     class Meta:
#         ordering = ["order", "id"]
#         verbose_name = _("Pack — Feature")
#         verbose_name_plural = _("Pack — Features")
#         indexes = [
#             models.Index(fields=["package", "order"]),
#         ]

#     def __str__(self) -> str:
#         return self.label







# # economic/services/models/service_package.py
# from __future__ import annotations

# from decimal import Decimal

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django.utils.text import slugify

# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .service import Service


# class ServicePackage(TranslatableModel):
#     """
#     ✅ Conserve ton existant :
#     - TranslatableModel + TranslatedFields
#     - CKEditor5Field
#     - slug nullable/unique
#     - M2M services
#     - total_price
#     - is_active
#     - created_at/updated_at

#     ✅ Ajouts "prod" safe :
#     - BillingPeriod: YEARLY/MONTHLY/ONE_TIME/CUSTOM
#     - Tier: STARTER/BUSINESS/PREMIUM/CUSTOM
#     - SupportLevel: STANDARD/PRIORITY/DEDICATED
#     - Currency EUR/XOF
#     - order + is_featured
#     - options pack (domain/ssl/emails/pages)
#     - SEO + tagline + CTA (translations)
#     - features (bullet list) via ServicePackageFeature
#     - slug auto si vide (safe)
#     """

#     # ==========================================================
#     # CONSTANTS PROD (ce que tu as listé)
#     # ==========================================================
#     class BillingPeriod(models.TextChoices):
#         YEARLY = "yearly", _("Annuel")
#         MONTHLY = "monthly", _("Mensuel")
#         ONE_TIME = "one_time", _("Ponctuel")
#         CUSTOM = "custom", _("Sur devis")

#     class Tier(models.TextChoices):
#         STARTER = "starter", _("Starter")
#         BUSINESS = "business", _("Business")
#         PREMIUM = "premium", _("Premium")
#         CUSTOM = "custom", _("Sur mesure")

#     class SupportLevel(models.TextChoices):
#         STANDARD = "standard", _("Standard")
#         PRIORITY = "priority", _("Prioritaire")
#         DEDICATED = "dedicated", _("Dédié")

#     class Currency(models.TextChoices):
#         EUR = "EUR", "EUR"
#         XOF = "XOF", "XOF"

#     translations = TranslatedFields(
#         name=models.CharField(max_length=200, verbose_name=_("Nom du pack")),
#         description=CKEditor5Field(blank=True, verbose_name=_("Description")),

#         # ✅ Ajouts prod (facultatifs, safe)
#         tagline=models.CharField(max_length=220, blank=True, verbose_name=_("Accroche")),
#         cta_label=models.CharField(
#             max_length=40,
#             blank=True,
#             default=_("Demander un devis"),
#             verbose_name=_("Libellé du bouton (CTA)"),
#         ),
#         seo_title=models.CharField(max_length=70, blank=True, verbose_name=_("SEO title")),
#         seo_description=models.CharField(max_length=160, blank=True, verbose_name=_("SEO description")),
#     )

#     slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

#     services = models.ManyToManyField(
#         Service,
#         related_name="packages",
#         blank=True,
#         verbose_name=_("Services inclus"),
#     )

#     total_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Prix total"),
#     )

#     # ✅ Ajouts PROD (safe)
#     tier = models.CharField(
#         max_length=16,
#         choices=Tier.choices,
#         default=Tier.STARTER,
#         verbose_name=_("Niveau"),
#     )

#     billing_period = models.CharField(
#         max_length=16,
#         choices=BillingPeriod.choices,
#         default=BillingPeriod.YEARLY,
#         verbose_name=_("Périodicité"),
#     )

#     currency = models.CharField(
#         max_length=3,
#         choices=Currency.choices,
#         default=Currency.EUR,
#         verbose_name=_("Devise"),
#     )

#     support_level = models.CharField(
#         max_length=16,
#         choices=SupportLevel.choices,
#         default=SupportLevel.STANDARD,
#         verbose_name=_("Support"),
#     )

#     included_domain_year = models.BooleanField(default=False, verbose_name=_("Nom de domaine (1 an) inclus"))
#     included_ssl = models.BooleanField(default=True, verbose_name=_("SSL inclus"))
#     emails_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre d’e-mails pro"))
#     max_pages = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pages max (si applicable)"))

#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
#     order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre d’affichage"))

#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

#     created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Pack de services")
#         verbose_name_plural = _("Packs de services")
#         ordering = ["-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["is_active", "is_featured", "order"]),
#             models.Index(fields=["tier", "billing_period", "currency"]),
#         ]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"Pack #{self.pk}"

#     # ✅ slug auto (safe) — seulement si slug vide
#     def _base_slug_source(self) -> str:
#         return (self.safe_translation_getter("name", any_language=True) or "").strip()

#     def _ensure_unique_slug(self):
#         if self.slug:
#             return
#         base = slugify(self._base_slug_source()) or "pack"
#         slug = base
#         i = 2
#         Model = self.__class__
#         while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#             slug = f"{base}-{i}"
#             i += 1
#         self.slug = slug

#     def save(self, *args, **kwargs):
#         if not self.pk and not self.slug:
#             super().save(*args, **kwargs)
#         self._ensure_unique_slug()
#         super().save(*args, **kwargs)

#     # Helpers SEO safe
#     def get_seo_title(self) -> str:
#         return (
#             self.safe_translation_getter("seo_title", any_language=True)
#             or self.safe_translation_getter("name", any_language=True)
#             or ""
#         )

#     def get_seo_description(self) -> str:
#         return (
#             self.safe_translation_getter("seo_description", any_language=True)
#             or self.safe_translation_getter("tagline", any_language=True)
#             or ""
#         )

#     def formatted_price(self) -> str:
#         if self.billing_period == self.BillingPeriod.CUSTOM:
#             return _("Sur devis")
#         return f"{self.total_price:g} {self.currency}"


# class ServicePackageFeature(models.Model):
#     """
#     ✅ Nouveau modèle (safe) : bullets/points d’un Pack (admin-driven).
#     """
#     package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name="features")
#     label = models.CharField(max_length=220, verbose_name=_("Élément"))
#     is_highlight = models.BooleanField(default=False, verbose_name=_("Mettre en évidence"))
#     order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre"))

#     class Meta:
#         ordering = ["order", "id"]
#         verbose_name = _("Pack — Feature")
#         verbose_name_plural = _("Pack — Features")
#         indexes = [
#             models.Index(fields=["package", "order"]),
#         ]

#     def __str__(self) -> str:
#         return self.label







# # economic/services/models/service_package.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .service import Service


# class ServicePackage(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=200,
#             verbose_name=_("Nom du pack"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     slug = models.SlugField(
#         unique=True,
#         blank=True,
#         null=True,
#         verbose_name=_("Slug"),
#     )

#     services = models.ManyToManyField(
#         Service,
#         related_name="packages",
#         blank=True,
#         verbose_name=_("Services inclus"),
#     )

#     total_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Prix total"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         editable=False,
#         verbose_name=_("Créé le"),
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Pack de services")
#         verbose_name_plural = _("Packs de services")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"Pack #{self.pk}"






# # economic/services/models/service_package.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .service import Service


# class ServicePackage(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=255,
#             verbose_name=_("Nom du pack"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     slug = models.SlugField(
#         max_length=255,
#         unique=True,
#         verbose_name=_("Slug"),
#     )

#     services = models.ManyToManyField(
#         Service,
#         related_name="packages",
#         blank=True,
#         verbose_name=_("Services inclus"),
#     )

#     total_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Prix du pack"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
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
#         verbose_name = _("Pack de services")
#         verbose_name_plural = _("Packs de services")
#         ordering = ["slug", "id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)
