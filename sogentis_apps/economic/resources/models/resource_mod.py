# economic/resources/models/resource_mod.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .resource_category import ResourceCategory
from django.utils import timezone


class ResourceMod(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        summary=models.TextField(blank=True, verbose_name=_("Résumé")),
        content=CKEditor5Field(blank=True, verbose_name=_("Contenu")),
    )

    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.PROTECT,
        related_name="resources",
        null=True,
        blank=True,
        verbose_name=_("Catégorie"),
    )

    slug = models.SlugField(max_length=255, blank=True, null=True)
    is_published = models.BooleanField(default=True, verbose_name=_("Publié"))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Ressource")
        verbose_name_plural = _("Ressources")
        ordering = ["-created_at"]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Resource #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.safe_translation_getter("title", any_language=True) or "ressource"
            self.slug = slugify(base)[:255]
        super().save(*args, **kwargs)
