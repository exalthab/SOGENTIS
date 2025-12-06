#about/models/mother.py
from django.db import models
from django.utils import timezone
from parler.models import TranslatableModel, TranslatedFields


class Mother(TranslatableModel):
    """
    Modèle Mère — version ONG professionnelle
    Compatible Django Parler + multilingue.
    Conçu pour affichage sur site (À propos / bénéficiaires).
    """

    # 🔹 Champs traduisibles
    translations = TranslatedFields(
        name=models.CharField(max_length=150),
        story=models.TextField(blank=True),                      # Son histoire / témoignage
        activity=models.CharField(max_length=255, blank=True),   # Petit commerce / métier
    )

    # 🔹 Informations personnelles
    photo = models.ImageField(upload_to="mothers/")
    birth_date = models.DateField(null=True, blank=True)

    marital_status = models.CharField(
        max_length=50,
        choices=[
            ("single", "Célibataire"),
            ("married", "Mariée"),
            ("widow", "Veuve"),
            ("separated", "Séparée"),
        ],
        blank=True,
        null=True
    )

    number_of_children = models.PositiveIntegerField(default=0)

    # 🔹 Informations économiques (logique ONG)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="XOF")

    support_needed = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Ex: capital de commerce, formation, logement..."
    )

    # ⭐ NOUVEAU : Montant du capital demandé
    capital_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Montant du capital requis pour autonomisation."
    )

    # 🔹 Données administratives
    country = models.CharField(max_length=100, blank=True, null=True)
    identification_number = models.CharField(max_length=100, blank=True, null=True)

    @property
    def age(self):
        """Calcule l'âge exact comme pour les enfants."""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)



