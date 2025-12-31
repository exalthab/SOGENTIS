# donations/services/donor_stats.py

from django.db.models import Sum, Count
from donations.models import Donation


class DonorStatsService:
    @staticmethod
    def for_user(user) -> dict:
        """
        Retourne les statistiques de dons pour un utilisateur donné.
        """

        donations = Donation.objects.filter(
            user=user,
            status=Donation.STATUS_COMPLETED
        )

        stats = donations.aggregate(
            total_amount=Sum("amount"),
            total_donations=Count("id"),
        )

        return {
            "total_amount": stats["total_amount"] or 0,
            "total_donations": stats["total_donations"] or 0,
        }
