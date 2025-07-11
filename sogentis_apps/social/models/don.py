# # social/models/don.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Don(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur")
    )
    montant = models.DecimalField(_("Montant"), max_digits=10, decimal_places=2)
    date = models.DateTimeField(_("Date du don"), auto_now_add=True)

    class Meta:
        verbose_name = _("Don (simple)")
        verbose_name_plural = _("Dons (simples)")
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} – {self.montant} FCFA le {self.date.strftime('%d/%m/%Y %H:%M')}"
