# social/models/project.py

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

    goal = models.DecimalField(
        _("Objectif du projet (FCFA)"),
        max_digits=12,
        decimal_places=2,
        default=1000000
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

    # ---------------------------------------------------------
    # 🔹 Montant total collecté pour le projet
    # ---------------------------------------------------------
    def total_collected(self):
        """
        Somme totale des dons payés pour ce projet.
        Aligné avec Donation.project.related_name = 'donations'
        """
        total = self.donations.filter(status="paid").aggregate(
            total=Sum("amount")
        )["total"]

        return float(total or 0.0)

    # ---------------------------------------------------------
    # 🔹 Pourcentage atteint par rapport à l'objectif
    # ---------------------------------------------------------
    def percentage_collected(self):
        """
        Calcule le pourcentage de l’objectif atteint.
        Retourne un nombre entre 0 et 100.
        """
        goal = float(self.goal or 0)
        if goal <= 0:
            return 0.0

        collected = self.total_collected()
        percent = (collected / goal) * 100

        # On limite à 100% maximum
        return min(round(percent, 2), 100.0)
