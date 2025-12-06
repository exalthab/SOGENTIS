from django.db import models
from parler.models import TranslatableModel, TranslatedFields

class Organigram(TranslatableModel):
    """
    Modèle pour stocker l'organigramme de l'équipe.
    """
    image = models.ImageField(upload_to="team/organigram/")
    
    translations = TranslatedFields(
        title=models.CharField(max_length=255, blank=True),
        description=models.TextField(blank=True),
    )

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or "Organigramme"
