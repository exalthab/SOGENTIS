from donations.models import Donation
from django.db.models import Sum


class DonorDashboardService:

    @staticmethod
    def get_donor_stats(user):
        donations = Donation.objects.filter(
            user=user,
            status="CONFIRMED"
        )

        return {
            "total_donations": donations.count(),
            "total_amount": donations.aggregate(
                total=Sum("amount")
            )["total"] or 0,
            "recent_donations": donations.order_by("-created_at")[:5],
        }
