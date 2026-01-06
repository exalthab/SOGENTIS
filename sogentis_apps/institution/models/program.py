from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from institution.models.base import TimeStampedModel
from institution.models.facility import Facility


class Program(TimeStampedModel):
    """
    Programme/activité lié(e) à une structure :
    - cours, ateliers, projets éducatifs
    - campagnes santé
    - activités jeunesse, sport, culture
    """

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="programs",
        verbose_name=_("Structure"),
    )

    title = models.CharField(_("Titre"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, blank=True)

    summary = models.CharField(_("Résumé"), max_length=280, blank=True, default="")
    content = models.TextField(_("Contenu"), blank=True, default="")

    start_date = models.DateField(_("Date début"), null=True, blank=True)
    end_date = models.DateField(_("Date fin"), null=True, blank=True)

    is_active = models.BooleanField(_("Actif"), default=True, db_index=True)

    class Meta:
        verbose_name = _("Programme")
        verbose_name_plural = _("Programmes")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "programme"
            candidate = base
            i = 2
            while Program.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)
