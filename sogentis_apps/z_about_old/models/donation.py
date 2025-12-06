#about/models/donation.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Donation(models.Model):
    """
    Représente un don effectué par un sponsor / donateur.
    """

    sponsor = models.ForeignKey(
        "about.Sponsor",
        on_delete=models.CASCADE,
        related_name="donations",
        verbose_name=_("Sponsor / Donateur"),
    )
    amount = models.DecimalField(_("Montant (FCFA)"), max_digits=12, decimal_places=2)
    recurring = models.BooleanField(_("Don récurrent"), default=False)
    message = models.TextField(_("Message ou remarque"), blank=True)

    date = models.DateTimeField(_("Date du don"), auto_now_add=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Don")
        verbose_name_plural = _("Dons")

    def __str__(self):
        return f"{self.sponsor.name} – {self.amount} FCFA"





# #about/models/donation.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Donation(models.Model):
#     sponsor = models.ForeignKey(
#         "about.Sponsor",
#         on_delete=models.CASCADE,
#         related_name="donations",
#         verbose_name=_("Sponsor"),
#     )
#     amount = models.DecimalField(_("Montant (FCFA)"), max_digits=12, decimal_places=2)
#     date = models.DateTimeField(_("Date du don"), auto_now_add=True)
#     recurring = models.BooleanField(_("Don récurrent"), default=False)
#     message = models.TextField(_("Message"), blank=True)

#     class Meta:
#         ordering = ["-date"]
#         verbose_name = _("Don")
#         verbose_name_plural = _("Dons")

#     def __str__(self):
#         return f"{self.sponsor.name} - {self.amount} FCFA"
