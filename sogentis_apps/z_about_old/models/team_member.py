# about/models/team_member.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django.utils.timezone import now


class TeamMember(TranslatableModel):
    """
    Membre de l’équipe affiché sur la page À propos.
    """

    about_page = models.ForeignKey(
        "about.AboutPage",
        on_delete=models.CASCADE,
        related_name="team_members",
        verbose_name=_("Page À propos"),
        null=True,
        blank=True,
    )

    translations = TranslatedFields(
        name=models.CharField(_("Nom complet"), max_length=200),
        role=models.CharField(_("Rôle ou fonction"), max_length=200),
        bio=models.TextField(_("Biographie"), blank=True),
    )

    photo = models.ImageField(_("Photo"), upload_to="about/team/", blank=True, null=True)
    email = models.EmailField(_("Adresse e-mail"), blank=True, null=True)
    linkedin = models.URLField(_("Profil LinkedIn"), blank=True, null=True)
    twitter = models.URLField(_("Profil Twitter"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Membre de l’équipe")
        verbose_name_plural = _("Membres de l’équipe")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or _("Membre sans nom")



# #about/models/team_member.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# class TeamMember(TranslatableModel):
#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         on_delete=models.CASCADE,
#         related_name="team_members",
#         verbose_name=_("Page À propos"),
#         null=True,
#         blank=True
#     )

#     translations = TranslatedFields(
#         name=models.CharField(_("Nom complet"), max_length=200),
#         role=models.CharField(_("Rôle"), max_length=200),
#         bio=models.TextField(_("Biographie"), blank=True),
#     )

#     photo = models.ImageField(_("Photo"), upload_to="about/team/", blank=True, null=True)
#     email = models.EmailField(_("Email"), blank=True, null=True)
#     linkedin = models.URLField(_("Profil LinkedIn"), blank=True, null=True)
#     twitter = models.URLField(_("Profil Twitter"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = _("Membre d’équipe")
#         verbose_name_plural = _("Équipe")

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or "—"










# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from .about_page import AboutPage



# class TeamMember(models.Model):
#     about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name="team_members", null=True, blank=True)
#     name = models.CharField(_("Nom complet"), max_length=200)
#     role = models.CharField(_("Rôle"), max_length=200)
#     bio = models.TextField(_("Biographie"), blank=True)
#     photo = models.ImageField(_("Photo"), upload_to="about/team/", blank=True, null=True)
#     email = models.EmailField(_("Email"), blank=True, null=True)
#     linkedin = models.URLField(_("Profil LinkedIn"), blank=True, null=True)
#     twitter = models.URLField(_("Profil Twitter"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
#     is_active = models.BooleanField(default=True)  # ✅ ajout
#     # created_at = models.DateTimeField(auto_now_add=True)
#     # updated_at = models.DateTimeField(auto_now=True)
#     class Meta:
#         ordering = ["order"]
#         verbose_name = _("Membre d’équipe")
#         verbose_name_plural = _("Équipe")

#     def __str__(self):
#         return self.name
