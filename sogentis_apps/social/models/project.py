from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum


class Project(models.Model):
    title = models.CharField(_("Nom du projet"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(
        _("Image illustrative"),
        upload_to="projects/images/",
        blank=True,
        null=True
    )
    goal = models.DecimalField(  # 👈 Nom conservé comme demandé
        _("Objectif du projet (FCFA)"),
        max_digits=12,
        decimal_places=2,
        default=1000000  # 👈 Défaut ajouté pour éviter les erreurs à la migration
    )
    is_active = models.BooleanField(_("Projet actif ?"), default=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Dernière modification"), auto_now=True)

    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def total_collected(self):
        total = self.donation_set.filter(status="paid").aggregate(
            total=Sum("amount")
        )["total"]
        try:
            return float(total) if total is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def percentage_collected(self):
        try:
            if self.goal and float(self.goal) > 0:
                percent = (self.total_collected() / float(self.goal)) * 100
                return min(percent, 100.0)
        except (ValueError, ZeroDivisionError, TypeError):
            pass
        return 0.0
