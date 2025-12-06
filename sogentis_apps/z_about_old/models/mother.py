#about/models/mother.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Mother(models.Model):
    """
    Représente une mère bénéficiaire soutenue par l’association.
    """

    name = models.CharField(_("Nom complet"), max_length=255)
    children_count = models.PositiveIntegerField(_("Nombre d’enfants à charge"), default=0)
    story = models.TextField(_("Témoignage / Histoire personnelle"), blank=True)
    photo = models.ImageField(_("Photo"), upload_to="about/mothers/", blank=True, null=True)
    is_active = models.BooleanField(_("Active"), default=True)
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)

    created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mise à jour le"), auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Maman bénéficiaire")
        verbose_name_plural = _("Mamans bénéficiaires")

    def __str__(self):
        return self.name or _("Maman sans nom")




# # about/models/mother.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Mother(models.Model):
#     name = models.CharField(_("Nom de la mère"), max_length=255)
#     children_count = models.PositiveIntegerField(_("Nombre d’enfants"), default=0)
#     story = models.TextField(_("Témoignage / Histoire"), blank=True)
#     photo = models.ImageField(
#         _("Photo"), upload_to="about/mothers/", blank=True, null=True
#     )
#     is_active = models.BooleanField(_("Active"), default=True)

#     # 🕒 Added timestamps to match admin configuration
#     created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mise à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Maman bénéficiaire")
#         verbose_name_plural = _("Mamans bénéficiaires")

#     def __str__(self):
#         return self.name
