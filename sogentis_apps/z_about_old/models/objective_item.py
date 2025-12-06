# about/models/objective_item.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class ObjectiveItem(TranslatableModel):
    """
    Représente un objectif associé à la page À propos.
    """

    translations = TranslatedFields(
        title=models.CharField(_("Titre de l’objectif"), max_length=150),
        description=models.TextField(_("Description"), blank=True),
    )

    about_page = models.ForeignKey(
        "about.AboutPage",
        related_name="objectives",
        on_delete=models.CASCADE,
        verbose_name=_("Page À propos")
    )

    icon = models.CharField(_("Icône (CSS ou nom)"), max_length=100, blank=True)
    image = models.ImageField(
        _("Image"),
        upload_to="about/objectives/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Objectif")
        verbose_name_plural = _("Objectifs")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Objectif #{self.id}"






# #about/models/objective.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# class ObjectiveItem(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )

#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         related_name="objectives",
#         on_delete=models.CASCADE,
#         verbose_name="Page À propos"
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/objectives/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Objectif"
#         verbose_name_plural = "Objectifs"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Objectif #{self.id}"




# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class Objective(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         description=models.TextField(_("Description")),
#     )
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)



# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Objective(models.Model):
#     title = models.CharField(_("Objectif"), max_length=255)
#     description = models.TextField(_("Description"), blank=True)
#     icon = models.CharField(_("Icône"), max_length=100, blank=True)
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")

#     def __str__(self):
#         return self.title
