# economic/formations/models/module.py
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .base import TimeStampedModel
from .course import Course


class Module(TimeStampedModel, TranslatableModel):
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

    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")
        ordering = ["course_id", "order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="uniq_module_order_per_course"),
        ]
        indexes = [
            models.Index(fields=["course", "order"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Module {self.pk}"




# # economic/formations/models/module.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .base import TimeStampedModel
# from .course import Course


# class Module(TimeStampedModel, TranslatableModel):
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="modules",
#         verbose_name=_("Formation"),
#     )

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         description=CKEditor5Field(blank=True, verbose_name=_("Description")),
#     )

#     order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = _("Module")
#         verbose_name_plural = _("Modules")
#         ordering = ["order", "id"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Module {self.pk}"





# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .course import Course


# class Module(TranslatableModel):
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="modules",
#         verbose_name=_("Formation"),
#     )

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         description=CKEditor5Field(blank=True, verbose_name=_("Description")),
#     )

#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         verbose_name = _("Module")
#         verbose_name_plural = _("Modules")
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)
