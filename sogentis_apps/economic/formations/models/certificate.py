# economic/formations/models/certificate.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .course import Course
from .enrollment import Enrollment


class Certificate(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="certificate",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_("Formation"),
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Certificat")
        verbose_name_plural = _("Certificats")

    def __str__(self):
        return f"Certificat {self.course}"
