# about/models/partner.py
from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Partner(TranslatableModel):
    """
    Représente un partenaire de l'ONG ou de l'organisation.
    Compatible avec Django Parler pour les champs traduisibles.
    """

    # 🔹 Champs traduisibles
    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            help_text="Nom du partenaire"
        ),
        description=models.TextField(
            blank=True,
            help_text="Description ou informations supplémentaires sur le partenaire"
        )
    )

    # 🔹 Logo et site web
    logo = models.ImageField(
        upload_to='partners/',
        blank=True,
        null=True,
        help_text="Logo du partenaire"
    )
    website = models.URLField(
        blank=True,
        null=True,
        help_text="URL du site web du partenaire"
    )

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Partenaire"

    @property
    def logo_url(self):
        """
        Retourne l'URL du logo ou une image par défaut si aucune image.
        """
        if self.logo and hasattr(self.logo, "url"):
            return self.logo.url
        return "/static/img/default-partner.png"

