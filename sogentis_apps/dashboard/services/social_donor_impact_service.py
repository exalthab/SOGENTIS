from django.db.models import Sum, Count
from donations.models import Donation


class DonorImpactService:
    @staticmethod
    def by_project(user):
        """
        Agrège l'impact des dons du donateur par projet
        """
        qs = (
            Donation.objects
            .filter(user=user, status="CONFIRMED", project__isnull=False)
            .values(
                "project_id",
                "project__name",
                "project__slug",
                "project__goal_amount",   # si existe
            )
            .annotate(
                total_amount=Sum("amount"),
                donations_count=Count("id"),
            )
            .order_by("-total_amount")
        )

        impact = []
        for row in qs:
            goal = row.get("project__goal_amount") or 0
            total = row["total_amount"] or 0
            percent = int((total / goal) * 100) if goal else None

            impact.append({
                "project_id": row["project_id"],
                "project_name": row["project__name"],
                "project_slug": row["project__slug"],
                "total_amount": total,
                "donations_count": row["donations_count"],
                "goal_amount": goal,
                "percent": percent,
            })

        return impact
