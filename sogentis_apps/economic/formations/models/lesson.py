# economic/formations/models/lesson.py
from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .base import TimeStampedModel
from .module import Module


class Lesson(TimeStampedModel, TranslatableModel):
    class Type(models.TextChoices):
        VIDEO = "video", _("Vidéo")
        ARTICLE = "article", _("Article")
        QUIZ = "quiz", _("Quiz")
        LIVE = "live", _("Live")

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Module"),
    )

    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        content=CKEditor5Field(verbose_name=_("Contenu"), blank=True),
    )

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.VIDEO, verbose_name=_("Type"))

    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

    # accès / preview
    is_preview = models.BooleanField(default=False, verbose_name=_("Leçon gratuite (preview)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    # vidéo / live
    video_url = models.URLField(blank=True, verbose_name=_("URL vidéo"))
    video_file = models.FileField(
        upload_to="formations/lessons/videos/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_("Fichier vidéo"),
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Durée (secondes)"),
    )

    # pièces jointes
    attachment = models.FileField(
        upload_to="formations/lessons/attachments/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_("Pièce jointe"),
    )

    released_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Disponible à partir de"))

    class Meta:
        verbose_name = _("Leçon")
        verbose_name_plural = _("Leçons")
        ordering = ["module_id", "order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["module", "order"], name="uniq_lesson_order_per_module"),
        ]
        indexes = [
            models.Index(fields=["module", "order"]),
            models.Index(fields=["is_preview"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Lesson {self.pk}"

    @property
    def course(self):
        # pratique : lesson.course (sans FK directe)
        return self.module.course





# # economic/formations/models/lesson.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .base import TimeStampedModel
# from .module import Module


# class Lesson(TimeStampedModel, TranslatableModel):
#     module = models.ForeignKey(
#         Module,
#         on_delete=models.CASCADE,
#         related_name="lessons",
#         verbose_name=_("Module"),
#     )

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         content=CKEditor5Field(verbose_name=_("Contenu"), blank=True),
#     )

#     order = models.PositiveIntegerField(default=0)
#     video_url = models.URLField(blank=True)
#     attachment = models.FileField(upload_to="formations/lessons/", blank=True, null=True)

#     is_active = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = _("Leçon")
#         verbose_name_plural = _("Leçons")
#         ordering = ["order", "id"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Lesson {self.pk}"






# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .module import Module


# class Lesson(TranslatableModel):
#     module = models.ForeignKey(
#         Module,
#         on_delete=models.CASCADE,
#         related_name="lessons",
#         verbose_name=_("Module"),
#     )

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         content=CKEditor5Field(verbose_name=_("Contenu")),
#     )

#     order = models.PositiveIntegerField(default=0)
#     video_url = models.URLField(blank=True)

#     class Meta:
#         verbose_name = _("Leçon")
#         verbose_name_plural = _("Leçons")
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)
