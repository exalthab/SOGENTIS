# social/managers.py
from django.db import models
from django.db.models import Sum

class DonationManager(models.Manager):
    def aggregate_total_amount(self, only_paid=True):
        """
        Retourne le total des montants de dons (float).
        Par défaut, ne prend en compte que les dons payés.
        """
        qs = self.get_queryset()
        if only_paid:
            qs = qs.filter(status="paid")
        total = qs.aggregate(total=Sum("amount"))["total"]
        try:
            return float(total) if total is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def by_user(self, user):
        """
        Retourne tous les dons pour un utilisateur donné.
        """
        return self.get_queryset().filter(user=user)
