# economic/resources/models/resource_category.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from parler.models import TranslatableModel, TranslatedFields


class ResourceCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=180, verbose_name=_("Nom")),
        description=models.TextField(blank=True, verbose_name=_("Description")),
    )

    slug = models.SlugField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Catégorie de ressource")
        verbose_name_plural = _("Catégories de ressources")
        ordering = ["-created_at"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"Category #{self.pk}"

    def save(self, *args, **kwargs):
        # ✅ évite prepopulated_fields sur champs traduits
        if not self.slug:
            base = self.safe_translation_getter("name", any_language=True) or "categorie"
            self.slug = slugify(base)[:200]
        super().save(*args, **kwargs)
