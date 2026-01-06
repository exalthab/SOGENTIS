from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from institution.models.base import TimeStampedModel


class Facility(TimeStampedModel):
    """
    Une structure institutionnelle locale :
    - école
    - centre de santé / hôpital
    - centre de loisirs / jeunesse
    - autre (future extension)
    """

    class FacilityType(models.TextChoices):
        SCHOOL = "SCHOOL", _("École")
        HEALTH = "HEALTH", _("Santé / Centre médical")
        YOUTH = "YOUTH", _("Jeunesse / Récréation")
        OTHER = "OTHER", _("Autre")

    name = models.CharField(_("Nom"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, blank=True)

    facility_type = models.CharField(
        _("Type"),
        max_length=20,
        choices=FacilityType.choices,
        default=FacilityType.OTHER,
        db_index=True,
    )

    short_description = models.CharField(_("Résumé"), max_length=280, blank=True, default="")
    description = models.TextField(_("Description"), blank=True, default="")

    address = models.CharField(_("Adresse"), max_length=255, blank=True, default="")
    city = models.CharField(_("Ville"), max_length=120, blank=True, default="")
    country = models.CharField(_("Pays"), max_length=80, blank=True, default="SN")

    phone = models.CharField(_("Téléphone"), max_length=50, blank=True, default="")
    email = models.EmailField(_("Email"), blank=True, default="")

    is_active = models.BooleanField(_("Actif"), default=True, db_index=True)

    class Meta:
        verbose_name = _("Structure")
        verbose_name_plural = _("Structures")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "structure"
            candidate = base
            i = 2
            while Facility.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)
