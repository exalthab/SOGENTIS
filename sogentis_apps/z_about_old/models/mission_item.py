#about/models/mission_item.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django.utils.timezone import now


class MissionItem(TranslatableModel):
    """
    Élément décrivant une mission de l’organisation (section de la page À propos).
    """

    translations = TranslatedFields(
        title=models.CharField(_("Titre"), max_length=150),
        description=models.TextField(_("Description"), blank=True),
    )

    about_page = models.ForeignKey(
        "about.AboutPage",
        related_name="missions",
        on_delete=models.CASCADE,
        verbose_name=_("Page À propos"),
    )
    icon = models.CharField(
        _("Icône (FontAwesome)"),
        max_length=100,
        blank=True,
        help_text=_("Exemple : fa-solid fa-hands-helping"),
    )
    image = models.ImageField(_("Image"), upload_to="about/missions/", blank=True, null=True)
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Mission")
        verbose_name_plural = _("Missions")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Mission #{self.id}"






# # about/models/mission_item.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# class MissionItem(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )

#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         related_name="missions",
#         on_delete=models.CASCADE,
#         verbose_name="Page À propos"
#     )
#     icon = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Nom d’icône FontAwesome (ex: fa-solid fa-hands-helping)"
#     )
#     image = models.ImageField(upload_to="about/missions/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Mission"
#         verbose_name_plural = "Missions"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Mission #{self.id}"
