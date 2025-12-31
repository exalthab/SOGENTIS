# economic/formations/models/module.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .course import Course


class Module(TranslatableModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("Formation"),
    )

    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        description=CKEditor5Field(blank=True, verbose_name=_("Description")),
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")
        ordering = ["order"]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)
