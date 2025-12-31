# economic/formations/models/lesson.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .module import Module


class Lesson(TranslatableModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Module"),
    )

    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        content=CKEditor5Field(verbose_name=_("Contenu")),
    )

    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True)

    class Meta:
        verbose_name = _("Leçon")
        verbose_name_plural = _("Leçons")
        ordering = ["order"]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)
