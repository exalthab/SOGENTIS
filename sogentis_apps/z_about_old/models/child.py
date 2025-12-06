#about/models/child.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Child(models.Model):
    """
    Représente un enfant bénéficiaire du programme d’aide.
    """

    class GenderChoices(models.TextChoices):
        MALE = "M", _("Garçon")
        FEMALE = "F", _("Fille")

    name = models.CharField(_("Nom de l’enfant"), max_length=255)
    gender = models.CharField(
        _("Sexe"),
        max_length=1,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
    )
    age = models.PositiveIntegerField(_("Âge"), default=0)
    school = models.CharField(_("École fréquentée"), max_length=255, blank=True, null=True)
    story = models.TextField(_("Histoire ou parcours"), blank=True)
    photo = models.ImageField(_("Photo"), upload_to="about/children/", blank=True, null=True)
    sponsored = models.BooleanField(_("Parrainé"), default=False)
    is_active = models.BooleanField(_("Actif"), default=True)
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Enfant bénéficiaire")
        verbose_name_plural = _("Enfants bénéficiaires")

    def __str__(self):
        return self.name or _("Enfant sans nom")




# # about/models/child.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Child(models.Model):
#     class GenderChoices(models.TextChoices):
#         MALE = "M", _("Garçon")
#         FEMALE = "F", _("Fille")

#     name = models.CharField(_("Nom de l’enfant"), max_length=255)
#     gender = models.CharField(
#         _("Sexe"),
#         max_length=1,
#         choices=GenderChoices.choices,
#         blank=True,
#         null=True,
#     )
#     age = models.PositiveIntegerField(_("Âge"), default=0)
#     school = models.CharField(_("École"), max_length=255, blank=True, null=True)
#     story = models.TextField(_("Histoire"), blank=True)
#     photo = models.ImageField(
#         _("Photo"), upload_to="about/children/", blank=True, null=True
#     )
#     sponsored = models.BooleanField(_("Parrainé"), default=False)
#     is_active = models.BooleanField(_("Actif"), default=True)

#     # 🕒 Add timestamps to match readonly_fields in admin
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")

#     def __str__(self):
#         return self.name





# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Child(models.Model):
#     name = models.CharField(_("Nom de l’enfant"), max_length=255)
#     age = models.PositiveIntegerField(_("Âge"), default=0)
#     story = models.TextField(_("Histoire"), blank=True)
#     photo = models.ImageField(_("Photo"), upload_to="about/children/", blank=True, null=True)
#     sponsored = models.BooleanField(_("Parrainé"), default=False)
#     is_active = models.BooleanField(default=True)  # ✅ ajout

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")

#     def __str__(self):
#         return self.name
