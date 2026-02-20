# economic/prestations/models/prestations_category.py
from __future__ import annotations

from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db import models

from parler.models import TranslatableModel, TranslatedFields


class PrestationCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=150, verbose_name=_("Nom")),
        description=models.TextField(blank=True, verbose_name=_("Description")),
        seo_title=models.CharField(max_length=70, blank=True, verbose_name=_("SEO title")),
        seo_description=models.CharField(max_length=160, blank=True, verbose_name=_("SEO description")),
    )

    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre d’affichage"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))

    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Catégorie de prestations")
        verbose_name_plural = _("Catégories de prestations")
        ordering = ["order", "-is_featured", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["is_active", "is_featured", "order"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or f"PrestationCategory #{self.pk}"

    def _base_slug_source(self) -> str:
        return (self.safe_translation_getter("name", any_language=True) or "").strip()

    def _ensure_unique_slug(self):
        if self.slug:
            return
        base = slugify(self._base_slug_source()) or "categorie"
        slug = base
        i = 2
        Model = self.__class__
        while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{i}"
            i += 1
        self.slug = slug

    def save(self, *args, **kwargs):
        # 2-pass save pour slug unique fiable même si traductions pas encore attachées
        if not self.pk and not self.slug:
            super().save(*args, **kwargs)
        self._ensure_unique_slug()
        super().save(*args, **kwargs)

    def get_seo_title(self) -> str:
        return (
            self.safe_translation_getter("seo_title", any_language=True)
            or self.safe_translation_getter("name", any_language=True)
            or ""
        )

    def get_seo_description(self) -> str:
        return (
            self.safe_translation_getter("seo_description", any_language=True)
            or self.safe_translation_getter("description", any_language=True)
            or ""
        )








# # economic/prestations/models/prestations_category.py
# from __future__ import annotations

# from django.db import models
# from django.utils import timezone
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _

# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(max_length=150, verbose_name=_("Nom")),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(max_length=70, blank=True, verbose_name=_("SEO title")),
#         seo_description=models.CharField(max_length=160, blank=True, verbose_name=_("SEO description")),
#     )

#     slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

#     is_active = models.BooleanField(default=True, verbose_name=_("Active"))

#     # ✅ Ajouts prod (pour tri stable / admin)
#     order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre d’affichage"))
#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))

#     created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         ordering = ["order", "-is_featured", "-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["is_active", "is_featured", "order"]),
#             models.Index(fields=["slug"]),
#         ]

#     def __str__(self) -> str:
#         return self.safe_translation_getter("name", any_language=True) or f"ServiceCategory #{self.pk}"

#     def _base_slug_source(self) -> str:
#         return (self.safe_translation_getter("name", any_language=True) or "").strip()

#     def _ensure_unique_slug(self):
#         if self.slug:
#             return
#         base = slugify(self._base_slug_source()) or "categorie"
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

#     def get_seo_title(self) -> str:
#         return (
#             self.safe_translation_getter("seo_title", any_language=True)
#             or self.safe_translation_getter("name", any_language=True)
#             or ""
#         )

#     def get_seo_description(self) -> str:
#         return (
#             self.safe_translation_getter("seo_description", any_language=True)
#             or self.safe_translation_getter("description", any_language=True)
#             or ""
#         )





# # economic/services/models/service_category.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django.utils.text import slugify

# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(max_length=150, verbose_name=_("Nom")),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#     )

#     slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("Slug"))

#     is_active = models.BooleanField(default=True, verbose_name=_("Active"))

#     created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"ServiceCategory #{self.pk}"

#     def _base_slug_source(self) -> str:
#         return (self.safe_translation_getter("name", any_language=True) or "").strip()

#     def _ensure_unique_slug(self):
#         if self.slug:
#             return
#         base = slugify(self._base_slug_source()) or "categorie"
#         slug = base
#         i = 2
#         Model = self.__class__
#         while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#             slug = f"{base}-{i}"
#             i += 1
#         self.slug = slug

#     def save(self, *args, **kwargs):
#         # 1er save pour obtenir pk si besoin
#         if not self.pk and not self.slug:
#             super().save(*args, **kwargs)
#         self._ensure_unique_slug()
#         super().save(*args, **kwargs)








# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     """
#     Catégorie de service (translatable via Django-Parler).
#     """

#     # ===============================
#     # CHAMPS TRADUITS
#     # ===============================
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=150,
#             verbose_name=_("Nom"),
#         ),
#         description=models.TextField(
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

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Active"),
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
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"ServiceCategory #{self.pk}"







# # economic/services/models/service_category.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=150,
#             verbose_name=_("Nom"),
#         ),
#         description=models.TextField(
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

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Active"),
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
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         ordering = ["-created_at", "-id"]  # ✅ plus d'erreur sur 'name'

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"ServiceCategory #{self.pk}"





# # economic/services/models/service_category.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=150,
#             verbose_name=_("Nom"),
#         ),
#     )

#     slug = models.SlugField(
#         max_length=200,
#         unique=True,
#         verbose_name=_("Slug"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Active"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mise à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         # ⚠️ PAS "name" (n’existe pas en base)
#         ordering = ("slug",)

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or self.slug
