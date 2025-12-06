#about/models/about_section.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class AboutSection(TranslatableModel):
    """
    Représente une section de la page À propos (historique, mission, vision, valeurs, équipe, etc.)
    """

    SECTION_CHOICES = [
        ("history", _("Historique")),
        ("mission", _("Mission")),
        ("vision", _("Vision")),
        ("values", _("Valeurs")),
        ("team", _("Équipe")),
    ]

    translations = TranslatedFields(
        title=models.CharField(_("Titre"), max_length=200),
        content=models.TextField(_("Contenu")),
    )

    section_type = models.CharField(
        _("Type de section"), max_length=20, choices=SECTION_CHOICES
    )
    image = models.ImageField(
        _("Image"), upload_to="about/images/", blank=True, null=True
    )
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
    is_active = models.BooleanField(
        _("Active"), default=True, help_text=_("Indique si la section doit être affichée.")
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Section À propos")
        verbose_name_plural = _("Sections À propos")
        ordering = ["order"]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or _("(Section)")







# #about/models/about_section.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class AboutSection(TranslatableModel):
#     SECTION_CHOICES = [
#         ("history", _("Historique")),
#         ("mission", _("Mission")),
#         ("vision", _("Vision")),
#         ("values", _("Nos valeurs")),
#         ("team", _("Notre équipe")),
#     ]

#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         content=models.TextField(_("Contenu")),
#     )

#     section_type = models.CharField(_("Type de section"), max_length=20, choices=SECTION_CHOICES)
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or _("(Section)")




# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class AboutSection(models.Model):
#     page = models.ForeignKey(
#         "about.AboutPage",
#         on_delete=models.CASCADE,
#         related_name="sections",
#         verbose_name=_("Page"),
#     )
#     title = models.CharField(_("Titre"), max_length=255)
#     content = models.TextField(_("Contenu"))
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
#     icon = models.CharField(_("Icône CSS"), max_length=100, blank=True)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = _("Section")
#         verbose_name_plural = _("Sections")

#     def __str__(self):
#         return f"{self.title} ({self.page})"
