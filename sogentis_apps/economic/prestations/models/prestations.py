# economic/prestations/models/prestations.py
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field
from parler.models import TranslatableModel, TranslatedFields


class Prestation(TranslatableModel):
    """
    Modèle Prestation – version production finale.

    ✔ Translatable (Parler)
    ✔ SEO-ready
    ✔ Front-friendly
    ✔ Évolutif (features, catégories, pricing)
    """

    # ==================================================
    # TYPE DE PRESTATION (PROD + compat valeurs historiques)
    # ==================================================
    class PrestationType(models.TextChoices):
        # Catégories PROD
        DESIGN = "design", _("Design & Communication")
        CLOUD = "cloud", _("Hébergement, Cloud & Infrastructure")
        DEV = "dev", _("Développement Web & Logiciels")
        AUTOMATION = "automation", _("Automatisation & Digitalisation")
        MANAGED = "managed", _("Maintenance IT & Infogérance")
        SECURITY = "security", _("Sécurité & Sauvegardes")

        # Valeurs historiques (compat)
        DIGITAL = "digital", _("Service numérique")
        PRINT = "print", _("Impression / Supports")
        EVENT = "event", _("Événementiel")
        MAINTENANCE = "maintenance", _("Maintenance / Support")

        OTHER = "other", _("Autre")

    # ==================================================
    # LIVRABLE
    # ==================================================
    class Deliverable(models.TextChoices):
        INVITATION_CARD = "invitation_card", _("Carte d’invitation")
        POSTER = "poster", _("Affiche")
        CALENDAR = "calendar", _("Calendrier")
        FLYER = "flyer", _("Flyer")
        BANNER = "banner", _("Bannière")
        LOGO = "logo", _("Logo")
        BROCHURE = "brochure", _("Brochure")
        OTHER = "other", _("Autre")

    # ==================================================
    # TRADUCTIONS + SEO
    # ==================================================
    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        short_description=models.CharField(max_length=300, blank=True, verbose_name=_("Résumé")),
        description=CKEditor5Field(blank=True, verbose_name=_("Description")),
        seo_title=models.CharField(max_length=70, blank=True, verbose_name=_("SEO title")),
        seo_description=models.CharField(max_length=160, blank=True, verbose_name=_("SEO description")),
    )

    # ==================================================
    # CHAMPS MÉTIER
    # ==================================================
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

    # ✅ IMPORTANT: FK vers PrestationCategory (pas ServiceCategory)
    category = models.ForeignKey(
        "prestations.PrestationCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prestations",
        verbose_name=_("Catégorie"),
    )

    prestation_type = models.CharField(
        max_length=20,
        choices=PrestationType.choices,
        default=PrestationType.OTHER,
        verbose_name=_("Type de prestation"),
    )

    deliverable = models.CharField(
        max_length=30,
        choices=Deliverable.choices,
        default=Deliverable.OTHER,
        verbose_name=_("Livrable"),
    )

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Prix de base"),
    )

    turnaround_days = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Délai (jours)"),
        help_text=_("Délai estimé de livraison."),
    )

    icon = models.CharField(
        max_length=80,
        blank=True,
        default="fa-solid fa-layer-group",
        verbose_name=_("Icône (FontAwesome)"),
        help_text=_("Ex: fa-solid fa-cloud, fa-solid fa-shield-halved"),
    )

    order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre d’affichage"))

    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))

    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Publié le"))

    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    # ==================================================
    # META
    # ==================================================
    class Meta:
        verbose_name = _("Prestation")
        verbose_name_plural = _("Prestations")
        ordering = ["-is_featured", "order", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_featured", "order"]),
            models.Index(fields=["prestation_type", "deliverable"]),
        ]

    # ==================================================
    # METHODS
    # ==================================================
    def __str__(self) -> str:
        return self.safe_translation_getter("title", any_language=True) or f"Prestation #{self.pk}"

    def _base_slug_source(self) -> str:
        return (self.safe_translation_getter("title", any_language=True) or "").strip()

    def _ensure_unique_slug(self):
        if self.slug:
            return
        base = slugify(self._base_slug_source()) or "prestation"
        slug = base
        i = 2
        Model = self.__class__
        while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{i}"
            i += 1
        self.slug = slug

    def save(self, *args, **kwargs):
        # 2-pass save conservé (slug unique fiable même si traductions attachées après)
        if not self.pk and not self.slug:
            super().save(*args, **kwargs)

        self._ensure_unique_slug()

        # Publication auto si actif
        if self.is_active and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    # ==================================================
    # SEO HELPERS
    # ==================================================
    def get_seo_title(self) -> str:
        return (
            self.safe_translation_getter("seo_title", any_language=True)
            or self.safe_translation_getter("title", any_language=True)
            or ""
        )

    def get_seo_description(self) -> str:
        return (
            self.safe_translation_getter("seo_description", any_language=True)
            or self.safe_translation_getter("short_description", any_language=True)
            or ""
        )


class PrestationFeature(models.Model):
    """
    Bullet points / features d’une prestation (admin-driven).
    """

    prestation = models.ForeignKey(
        Prestation,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("Prestation"),
    )
    label = models.CharField(max_length=220, verbose_name=_("Élément"))
    order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre"))

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Prestation — Feature")
        verbose_name_plural = _("Prestation — Features")
        indexes = [
            models.Index(fields=["prestation", "order"]),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------
# ✅ COMPAT (si tu as encore du code/templates qui importent Service/ServiceFeature)
# ---------------------------------------------------------------------
Service = Prestation
ServiceFeature = PrestationFeature







# # economic/prestations/models/prestations.py
# from __future__ import annotations

# from decimal import Decimal

# from django.db import models
# from django.utils import timezone
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _

# from django_ckeditor_5.fields import CKEditor5Field
# from parler.models import TranslatableModel, TranslatedFields


# class Service(TranslatableModel):
#     """
#     Modèle Service – version production finale.

#     ✔ Translatable (Parler)
#     ✔ SEO-ready
#     ✔ Rétro-compatible
#     ✔ UX / front-friendly
#     ✔ Évolutif (features, catégories, pricing)
#     """

#     # ==================================================
#     # TYPE DE SERVICE (RÉTRO + PROD)
#     # ==================================================
#     class ServiceType(models.TextChoices):
#         # Catégories PROD
#         DESIGN = "design", _("Design & Communication")
#         CLOUD = "cloud", _("Hébergement, Cloud & Infrastructure")
#         DEV = "dev", _("Développement Web & Logiciels")
#         AUTOMATION = "automation", _("Automatisation & Digitalisation")
#         MANAGED = "managed", _("Maintenance IT & Infogérance")
#         SECURITY = "security", _("Sécurité & Sauvegardes")

#         # Valeurs historiques (compat)
#         DIGITAL = "digital", _("Service numérique")
#         PRINT = "print", _("Impression / Supports")
#         EVENT = "event", _("Événementiel")
#         MAINTENANCE = "maintenance", _("Maintenance / Support")

#         OTHER = "other", _("Autre")

#     # ==================================================
#     # LIVRABLE
#     # ==================================================
#     class Deliverable(models.TextChoices):
#         INVITATION_CARD = "invitation_card", _("Carte d’invitation")
#         POSTER = "poster", _("Affiche")
#         CALENDAR = "calendar", _("Calendrier")
#         FLYER = "flyer", _("Flyer")
#         BANNER = "banner", _("Bannière")
#         LOGO = "logo", _("Logo")
#         BROCHURE = "brochure", _("Brochure")
#         OTHER = "other", _("Autre")

#     # ==================================================
#     # TRADUCTIONS + SEO
#     # ==================================================
#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         short_description=models.CharField(
#             max_length=300, blank=True, verbose_name=_("Résumé")
#         ),
#         description=CKEditor5Field(
#             blank=True, verbose_name=_("Description")
#         ),
#         seo_title=models.CharField(
#             max_length=70, blank=True, verbose_name=_("SEO title")
#         ),
#         seo_description=models.CharField(
#             max_length=160, blank=True, verbose_name=_("SEO description")
#         ),
#     )

#     # ==================================================
#     # CHAMPS MÉTIER
#     # ==================================================
#     slug = models.SlugField(
#         unique=True, blank=True, null=True, verbose_name=_("Slug")
#     )

#     category = models.ForeignKey(
#         "ServiceCategory",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="services",
#         verbose_name=_("Catégorie"),
#     )

#     service_type = models.CharField(
#         max_length=20,
#         choices=ServiceType.choices,
#         default=ServiceType.OTHER,
#         verbose_name=_("Type de service"),
#     )

#     deliverable = models.CharField(
#         max_length=30,
#         choices=Deliverable.choices,
#         default=Deliverable.OTHER,
#         verbose_name=_("Livrable"),
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Prix de base"),
#     )

#     turnaround_days = models.PositiveIntegerField(
#         default=3,
#         verbose_name=_("Délai (jours)"),
#         help_text=_("Délai estimé de livraison."),
#     )

#     icon = models.CharField(
#         max_length=80,
#         blank=True,
#         default="fa-solid fa-layer-group",
#         verbose_name=_("Icône (FontAwesome)"),
#         help_text=_("Ex: fa-solid fa-cloud, fa-solid fa-shield-halved"),
#     )

#     order = models.PositiveIntegerField(
#         default=100, verbose_name=_("Ordre d’affichage")
#     )

#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))

#     published_at = models.DateTimeField(
#         null=True, blank=True, verbose_name=_("Publié le")
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now, editable=False, verbose_name=_("Créé le")
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True, verbose_name=_("Mis à jour le")
#     )

#     # ==================================================
#     # META
#     # ==================================================
#     class Meta:
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ["-is_featured", "order", "-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["slug"]),
#             models.Index(fields=["is_active", "is_featured", "order"]),
#             models.Index(fields=["service_type", "deliverable"]),
#         ]

#     # ==================================================
#     # METHODS
#     # ==================================================
#     def __str__(self) -> str:
#         return (
#             self.safe_translation_getter("title", any_language=True)
#             or f"Service #{self.pk}"
#         )

#     def _base_slug_source(self) -> str:
#         return (
#             self.safe_translation_getter("title", any_language=True) or ""
#         ).strip()

#     def _ensure_unique_slug(self):
#         if self.slug:
#             return

#         base = slugify(self._base_slug_source()) or "service"
#         slug = base
#         i = 2
#         Model = self.__class__

#         while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#             slug = f"{base}-{i}"
#             i += 1

#         self.slug = slug

#     def save(self, *args, **kwargs):
#         # Double save initial conservé (slug unique fiable)
#         if not self.pk and not self.slug:
#             super().save(*args, **kwargs)

#         self._ensure_unique_slug()

#         # Publication auto si actif
#         if self.is_active and not self.published_at:
#             self.published_at = timezone.now()

#         super().save(*args, **kwargs)

#     # ==================================================
#     # SEO HELPERS
#     # ==================================================
#     def get_seo_title(self) -> str:
#         return (
#             self.safe_translation_getter("seo_title", any_language=True)
#             or self.safe_translation_getter("title", any_language=True)
#             or ""
#         )

#     def get_seo_description(self) -> str:
#         return (
#             self.safe_translation_getter("seo_description", any_language=True)
#             or self.safe_translation_getter("short_description", any_language=True)
#             or ""
#         )


# class ServiceFeature(models.Model):
#     """
#     Bullet points / features d’un service (admin-driven).
#     """

#     service = models.ForeignKey(
#         Service, on_delete=models.CASCADE, related_name="features"
#     )
#     label = models.CharField(max_length=220, verbose_name=_("Élément"))
#     order = models.PositiveIntegerField(
#         default=100, verbose_name=_("Ordre")
#     )

#     class Meta:
#         ordering = ["order", "id"]
#         verbose_name = _("Service — Feature")
#         verbose_name_plural = _("Service — Features")
#         indexes = [
#             models.Index(fields=["service", "order"]),
#         ]

#     def __str__(self) -> str:
#         return self.label







# # economic/services/models/service.py
# from __future__ import annotations

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django.utils.text import slugify

# from django_ckeditor_5.fields import CKEditor5Field
# from parler.models import TranslatableModel, TranslatedFields


# class Service(TranslatableModel):
#     """
#     ✅ Conserve ton existant :
#     - TranslatableModel + TranslatedFields
#     - CKEditor5Field
#     - slug non-translatable
#     - category FK "ServiceCategory"
#     - base_price, turnaround_days, is_active, is_featured
#     - logique de slug unique (ta logique conservée)

#     ✅ Ajouts "prod" safe :
#     - intégration des catégories DESIGN/CLOUD/DEV/AUTOMATION/MANAGED/SECURITY
#     - icon, order, published_at
#     - SEO (translations)
#     - features (bullet list) via ServiceFeature
#     """

#     # ==========================================================
#     # 1) TYPE DE SERVICE (INTÉGRATION DES CODES "PROD")
#     # ==========================================================
#     class ServiceType(models.TextChoices):
#         # ✅ tes catégories "prod"
#         DESIGN = "design", _("Design & Communication")
#         CLOUD = "cloud", _("Hébergement, Cloud & Infrastructure")
#         DEV = "dev", _("Développement Web & Logiciels")
#         AUTOMATION = "automation", _("Automatisation & Digitalisation")
#         MANAGED = "managed", _("Maintenance IT & Infogérance")
#         SECURITY = "security", _("Sécurité & Sauvegardes")

#         # ✅ tes valeurs existantes (compat)
#         DIGITAL = "digital", _("Service numérique")
#         PRINT = "print", _("Impression / Supports")
#         EVENT = "event", _("Événementiel")
#         MAINTENANCE = "maintenance", _("Maintenance / Support")
#         OTHER = "other", _("Autre")

#     SERVICE_TYPE_CHOICES = ServiceType.choices

#     # ==========================================================
#     # 2) LIVRABLES (TES CHOIX EXISTANTS CONSERVÉS)
#     # ==========================================================
#     class Deliverable(models.TextChoices):
#         INVITATION_CARD = "invitation_card", _("Carte d’invitation")
#         POSTER = "poster", _("Affiche")
#         CALENDAR = "calendar", _("Calendrier")
#         FLYER = "flyer", _("Flyer")
#         BANNER = "banner", _("Bannière")
#         LOGO = "logo", _("Logo")
#         BROCHURE = "brochure", _("Brochure")
#         OTHER = "other", _("Autre")

#     DELIVERABLE_CHOICES = Deliverable.choices

#     # ==========================================================
#     # 3) TRADUCTIONS (Parler + CKEditor5) + SEO (safe)
#     # ==========================================================
#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         short_description=models.CharField(max_length=300, blank=True, verbose_name=_("Résumé")),
#         description=CKEditor5Field(blank=True, verbose_name=_("Description")),

#         # ✅ Ajouts SEO (facultatifs, safe)
#         seo_title=models.CharField(max_length=70, blank=True, verbose_name=_("SEO title")),
#         seo_description=models.CharField(max_length=160, blank=True, verbose_name=_("SEO description")),
#     )

#     slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

#     category = models.ForeignKey(
#         "ServiceCategory",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="services",
#         verbose_name=_("Catégorie"),
#     )

#     service_type = models.CharField(
#         max_length=20,
#         choices=SERVICE_TYPE_CHOICES,
#         default=ServiceType.DIGITAL,
#         verbose_name=_("Type de service"),
#     )

#     deliverable = models.CharField(
#         max_length=30,
#         choices=DELIVERABLE_CHOICES,
#         default=Deliverable.OTHER,
#         verbose_name=_("Livrable"),
#     )

#     base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("Prix de base"))

#     turnaround_days = models.PositiveIntegerField(
#         default=3,
#         verbose_name=_("Délai (jours)"),
#         help_text=_("Délai estimé de livraison."),
#     )

#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))

#     # ✅ Ajouts PROD (safe)
#     icon = models.CharField(
#         max_length=80,
#         blank=True,
#         default="fa-solid fa-layer-group",
#         verbose_name=_("Icône (FontAwesome)"),
#         help_text=_("Ex: fa-solid fa-cloud, fa-solid fa-shield-halved"),
#     )
#     order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre d’affichage"))
#     published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Publié le"))

#     created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ["-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["is_active", "is_featured", "order"]),
#             models.Index(fields=["service_type", "deliverable"]),
#         ]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Service #{self.pk}"

#     def _base_slug_source(self) -> str:
#         return (self.safe_translation_getter("title", any_language=True) or "").strip()

#     def _ensure_unique_slug(self):
#         if self.slug:
#             return
#         base = slugify(self._base_slug_source()) or "service"
#         slug = base
#         i = 2
#         Model = self.__class__
#         while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#             slug = f"{base}-{i}"
#             i += 1
#         self.slug = slug

#     def save(self, *args, **kwargs):
#         # ✅ ta logique conservée (double save initial)
#         if not self.pk and not self.slug:
#             super().save(*args, **kwargs)

#         self._ensure_unique_slug()

#         # ✅ "published_at" auto si actif (safe)
#         if self.is_active and not self.published_at:
#             self.published_at = timezone.now()

#         super().save(*args, **kwargs)

#     # Helpers SEO safe (pas de dépendance urls)
#     def get_seo_title(self) -> str:
#         return (
#             self.safe_translation_getter("seo_title", any_language=True)
#             or self.safe_translation_getter("title", any_language=True)
#             or ""
#         )

#     def get_seo_description(self) -> str:
#         return (
#             self.safe_translation_getter("seo_description", any_language=True)
#             or self.safe_translation_getter("short_description", any_language=True)
#             or ""
#         )


# class ServiceFeature(models.Model):
#     """
#     ✅ Nouveau modèle (safe) : bullets/points d’un Service (admin-driven).
#     """
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="features")
#     label = models.CharField(max_length=220, verbose_name=_("Élément"))
#     order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre"))

#     class Meta:
#         ordering = ["order", "id"]
#         verbose_name = _("Service — Feature")
#         verbose_name_plural = _("Service — Features")
#         indexes = [
#             models.Index(fields=["service", "order"]),
#         ]

#     def __str__(self) -> str:
#         return self.label







# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django_ckeditor_5.fields import CKEditor5Field
# from parler.models import TranslatableModel, TranslatedFields


# class Service(TranslatableModel):
#     """
#     Modèle de service avec champs traduisibles via Django-Parler.
#     """

#     # ===============================
#     # CHAMPS TRADUITS
#     # ===============================
#     translations = TranslatedFields(
#         title=models.CharField(
#             max_length=255,
#             verbose_name=_("Titre"),
#         ),
#         short_description=models.CharField(
#             max_length=300,
#             blank=True,
#             verbose_name=_("Résumé"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     # ===============================
#     # CHAMPS PARTAGÉS (NON TRADUITS)
#     # ===============================
#     slug = models.SlugField(
#         unique=True,
#         blank=True,
#         null=True,
#         verbose_name=_("Slug"),
#     )

#     # 🔗 Lien vers ServiceCategory dans la même app
#     category = models.ForeignKey(
#         "ServiceCategory",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="services",
#         verbose_name=_("Catégorie"),
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Prix de base"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mis en avant"),
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
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Service #{self.pk}"








# # economic/services/models/service.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django_ckeditor_5.fields import CKEditor5Field
# from parler.models import TranslatableModel, TranslatedFields


# class Service(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(
#             max_length=255,
#             verbose_name=_("Titre"),
#         ),
#         short_description=models.CharField(
#             max_length=300,
#             blank=True,
#             verbose_name=_("Résumé"),
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

#     category = models.ForeignKey(
#         "services.ServiceCategory",  # ✅ STRING REFERENCE
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="services",
#         verbose_name=_("Catégorie"),
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Prix de base"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mis en avant"),
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
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Service #{self.pk}"








# # economic/services/models/service.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .service_category import ServiceCategory


# class Service(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(
#             max_length=255,
#             verbose_name=_("Titre"),
#         ),
#         short_description=models.CharField(
#             max_length=255,
#             blank=True,
#             verbose_name=_("Résumé"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     slug = models.SlugField(
#         max_length=200,
#         unique=True,
#         verbose_name=_("Slug"),
#     )

#     category = models.ForeignKey(
#         ServiceCategory,
#         on_delete=models.SET_NULL,
#         related_name="services",
#         null=True,
#         blank=True,
#         verbose_name=_("Catégorie"),
#     )

#     base_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         verbose_name=_("Prix de base"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mis en avant"),
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
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ("-created_at", "-id")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or self.slug
