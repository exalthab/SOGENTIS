# about/models/partner.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Partner(TranslatableModel):
    """
    Représente un partenaire associé à la page À propos.
    """

    about_page = models.ForeignKey(
        "about.AboutPage",
        on_delete=models.CASCADE,
        related_name="partners",
        verbose_name=_("Page À propos")
    )

    translations = TranslatedFields(
        name=models.CharField(_("Nom du partenaire"), max_length=255),
        description=models.TextField(_("Description"), blank=True),
    )

    logo = models.ImageField(_("Logo"), upload_to="about/partners/", blank=True, null=True)
    website = models.URLField(_("Site web"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Partenaire")
        verbose_name_plural = _("Partenaires")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or _("Partenaire sans nom")





# #about/models/partner.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from .about_page import AboutPage



# class Partner(TranslatableModel):
#     about_page = models.ForeignKey("about.AboutPage", on_delete=models.CASCADE, related_name="partners")
#     translations = TranslatedFields(
#         name=models.CharField(_("Nom du partenaire"), max_length=255),
#         description=models.TextField(_("Description"), blank=True),
#     )
#     logo = models.ImageField(_("Logo"), upload_to="about/partners/", blank=True, null=True)
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)