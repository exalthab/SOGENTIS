from django.db import models
from django.utils.translation import gettext_lazy as _

class Volunteer(models.Model):
    first_name = models.CharField(_("Prénom"), max_length=100)
    last_name = models.CharField(_("Nom"), max_length=100)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    motivation = models.TextField(_("Motivation"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Volontaire")
        verbose_name_plural = _("Volontaires")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
