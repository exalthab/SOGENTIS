#about/models/hero.py
from django.db import models
from parler.models import TranslatableModel, TranslatedFields

class HeroBlock(TranslatableModel):
    """Section Hero de la page À propos (bannière principale)."""

    background_image = models.ImageField(upload_to="about/hero/")
    
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        subtitle=models.TextField(blank=True),
        button_text=models.CharField(max_length=100, blank=True),
        button_link=models.URLField(blank=True),
    )

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)
