#about/models/sponsor.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Sponsor(models.Model):
    """
    Représente un sponsor ou donateur ayant soutenu un projet.
    """

    name = models.CharField(_("Nom du sponsor / donateur"), max_length=255)
    email = models.EmailField(_("Adresse e-mail"), blank=True, null=True)
    message = models.TextField(_("Message ou remarque"), blank=True)
    photo = models.ImageField(_("Photo / Logo"), upload_to="about/sponsors/", blank=True, null=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = _("Sponsor / Donateur")
        verbose_name_plural = _("Sponsors / Donateurs")

    def __str__(self):
        return self.name or _("Sponsor sans nom")





# #about/models/sponsor.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Sponsor(models.Model):
#     name = models.CharField(_("Nom du donateur / sponsor"), max_length=255)
#     email = models.EmailField(_("Email"), blank=True, null=True)
#     message = models.TextField(_("Message"), blank=True)
#     photo = models.ImageField(_("Photo / Logo"), upload_to="about/sponsors/", blank=True, null=True)
#     created_at = models.DateTimeField(_("Date d’ajout"), auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at"]
#         verbose_name = _("Sponsor / Donateur")
#         verbose_name_plural = _("Sponsors / Donateurs")

#     def __str__(self):
#         return self.name
