# economic/formations/models/section.py
from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from .module import Module


class Section(Module):
    """
    Alias/compat : Section = Module.
    Utile si tu veux exposer "sections" côté UI sans casser le modèle.
    """

    class Meta:
        proxy = True
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")





# # economic/formations/models/section.py
# from __future__ import annotations

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# from .base import TimeStampedModel
# from .course import Course


# class CourseSection(TimeStampedModel, TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#     )

#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections", verbose_name=_("Formation"))
#     order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

#     class Meta:
#         verbose_name = _("Section")
#         verbose_name_plural = _("Sections")
#         ordering = ["course_id", "order", "id"]
#         constraints = [
#             models.UniqueConstraint(fields=["course", "order"], name="uniq_section_order_per_course"),
#         ]

#     def __str__(self):
#         t = self.safe_translation_getter("title", any_language=True) or f"Section {self.order}"
#         return f"{self.course.slug} — {t}"
