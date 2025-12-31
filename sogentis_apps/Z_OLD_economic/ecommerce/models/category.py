# economic/ecommerce/models/category.py

from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _


class Category(TranslatableModel):
    """Catégories multi-langues pour les produits."""

    translations = TranslatedFields(
        name=models.CharField(_("Nom"), max_length=120),
        description=models.TextField(_("Description"), blank=True),
    )
    is_active = models.BooleanField(default=True)

    slug = models.SlugField(
        _("Slug"),
        max_length=180,
        unique=True,
        blank=True
    )

    icon = models.CharField(
        _("Icône"),
        max_length=100,
        blank=True,
        help_text=_("Nom d'icône CSS ou FontAwesome")
    )

    order = models.PositiveIntegerField(_("Ordre d'affichage"), default=0)

    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ["order", "slug"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or "Category"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.safe_translation_getter("name", any_language=True)) or "categorie"
            slug = base
            num = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)
