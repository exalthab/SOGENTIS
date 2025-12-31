from django.db import models
from django.utils.translation import gettext_lazy as _


class FAQCategory(models.Model):
    name = models.CharField(_("Nom"), max_length=120, unique=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Catégorie FAQ")
        verbose_name_plural = _("Catégories FAQ")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class FAQ(models.Model):
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
        verbose_name=_("Catégorie"),
    )

    question = models.CharField(_("Question"), max_length=220)
    answer = models.TextField(_("Réponse"))

    is_active = models.BooleanField(_("Actif"), default=True)
    sort_order = models.PositiveIntegerField(_("Ordre"), default=0)

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ["sort_order", "question"]
        indexes = [models.Index(fields=["is_active", "sort_order"])]

    def __str__(self) -> str:
        return self.question
