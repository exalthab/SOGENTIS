# economic/formations/models/category.py
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .base import TimeStampedModel


class CourseCategory(TimeStampedModel, TranslatableModel):
    """
    Domaine / catégorie de formation (multilingue).
    Utilisé pour organiser les cours et structurer le catalogue.
    """

    translations = TranslatedFields(
        name=models.CharField(
            max_length=120,
            verbose_name=_("Nom"),
        ),
        short_description=models.CharField(
            max_length=255,
            blank=True,
            verbose_name=_("Description courte"),
        ),
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre"),
        help_text=_("Ordre d’affichage dans les listes"),
    )

    class Meta:
        verbose_name = _("Domaine de formation")
        verbose_name_plural = _("Domaines de formation")
        ordering = ["order", "id"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or self.slug

    def save(self, *args, **kwargs):
        """
        Génère automatiquement un slug unique basé sur le nom traduit.
        Garantit l’unicité même en cas de doublons.
        """
        if not self.slug:
            base = (
                self.safe_translation_getter("name", any_language=True)
                or "category"
            )
            self.slug = slugify(base)[:140]

            original = self.slug
            i = 2
            while CourseCategory.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original}-{i}"[:140]
                i += 1

        super().save(*args, **kwargs)






# # economic/formations/models/category.py
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# from .base import TimeStampedModel


# class CourseCategory(TimeStampedModel, TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(max_length=120, verbose_name=_("Nom")),
#         short_description=models.CharField(max_length=255, blank=True, verbose_name=_("Description courte")),
#     )

#     slug = models.SlugField(max_length=140, unique=True, blank=True, verbose_name=_("Slug"))
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

#     class Meta:
#         verbose_name = _("Domaine de formation")
#         verbose_name_plural = _("Domaines de formation")
#         ordering = ["order", "id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or self.slug

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base = self.safe_translation_getter("name", any_language=True) or "category"
#             self.slug = slugify(base)[:140]

#             # garantit unicité
#             original = self.slug
#             i = 2
#             while CourseCategory.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
#                 self.slug = f"{original}-{i}"[:140]
#                 i += 1

#         super().save(*args, **kwargs)
