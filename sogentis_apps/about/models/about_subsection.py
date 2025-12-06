# about/models/about_subsection.py
from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field


class AboutSubsection(TranslatableModel):

    # Valeurs fixes (6 tabs possibles)
    SUBSECTION_CHOICES = [
        ("about", "À propos"),
        ("history", "Histoire"),
        ("vision", "Vision"),
        ("mission", "Mission"),
        ("objectives", "Objectifs"),
        ("values", "Valeurs"),
    ]

    key = models.CharField(
        max_length=30,
        choices=SUBSECTION_CHOICES,
        unique=True,
    )
    slug = models.SlugField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        subtitle=models.CharField(max_length=255, blank=True),
        content=CKEditor5Field(config_name="default", blank=True),
        image=models.ImageField(
            upload_to="about/subsections/",
            blank=True,
            null=True,
        ),
    )

    def save(self, *args, **kwargs):
        # Slug basé sur la clé si vide
        if not self.slug:
            self.slug = slugify(self.key)

        # ⚠️ Blindage : si l'image vaut False (case "Effacer" cochée),
        # on la remet proprement à None pour éviter les .name sur un booléen.
        img = getattr(self, "image", None)
        if isinstance(img, bool):
            self.image = None

        super().save(*args, **kwargs)

    def __str__(self):
        # Affiche le titre dans n'importe quelle langue dispo
        return self.safe_translation_getter("title", any_language=True) or self.key

