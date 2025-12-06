# about/models/child.py
from django.db import models
from django.utils import timezone
from parler.models import TranslatableModel, TranslatedFields

# Choices pour la classe / catégorie
CLASS_CHOICES = [
    ("CI", "CI"), ("CP", "CP"), ("CE1", "CE1"), ("CE2", "CE2"),
    ("CM1", "CM1"), ("CM2", "CM2"), ("BEPC", "BEPC"), ("BAC", "BAC"), ("TVET", "TVET"),
]

class Child(TranslatableModel):
    """
    Modèle représentant un enfant soutenu dans le programme SOGENTIS.
    Compatible avec le module de donation pour lier un don à un enfant spécifique.
    """
    # Champs traduisibles
    translations = TranslatedFields(
        name=models.CharField(max_length=100, help_text="Nom complet de l'enfant"),
        description=models.TextField(blank=True, help_text="Description ou notes sur l'enfant")
    )

    # Informations principales
    photo = models.ImageField(
        upload_to='children/',
        blank=True,
        null=True,
        help_text="Photo de l'enfant, affichée sur le formulaire et le reçu"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date de naissance de l'enfant"
    )

    # École et classe
    school_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nom de l'école fréquentée par l'enfant"
    )
    school_class = models.CharField(
        max_length=10,
        choices=CLASS_CHOICES,
        blank=True,
        null=True,
        help_text="Classe actuelle de l'enfant"
    )

    # Budget et devise
    annual_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Budget annuel nécessaire pour soutenir l'enfant"
    )
    currency = models.CharField(
        max_length=10,
        default="XOF",
        help_text="Devise utilisée pour le budget"
    )

    # Champs supplémentaires pour suivi administratif
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Pays de résidence de l'enfant"
    )
    identification_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Numéro d'identification ou matricule de l'enfant"
    )

    @property
    def age(self):
        """Calcule l'âge de l'enfant à partir de la date de naissance."""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Enfant sans nom"

    class Meta:
        verbose_name = "Enfant"
        verbose_name_plural = "Enfants"
        ordering = ['translations__name']  # Tri par nom pour les listes



