# about/models/team_member.py

from django.db import models
from parler.models import TranslatableModel, TranslatedFields

class TeamMember(TranslatableModel):
    """
    Membre de l'équipe avec support multilingue.
    Catégories :
    - board : Conseil d'administration
    - employee : Employé
    """

    CATEGORY_CHOICES = [
        ("board", "Conseil d'administration"),
        ("employee", "Employé"),
    ]

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        role=models.CharField(max_length=100),
        bio=models.TextField(blank=True),
    )

    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="board",
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)

    @property
    def photo_url(self):
        """
        Retourne la photo ou une image par défaut.
        Avant : .url cassait si photo vide → page blanche / boucle cassée.
        """
        if self.photo and hasattr(self.photo, "url"):
            return self.photo.url
        return "/static/img/default-profile.png"
