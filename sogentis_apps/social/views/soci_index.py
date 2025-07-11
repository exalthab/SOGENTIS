# social/views/soci_index.py

from django.shortcuts import render
from django.db.models import Sum
from social.models import Publication, Project, Donation, Engagement
from stakeholders.models.beneficiaries import Beneficiary

def soci_index_view(request):
    # 🔹 Projets actifs
    projects = Project.objects.filter(is_active=True)
    total_projects = projects.count()

    # 🔹 Publications publiques
    publications = Publication.objects.filter(is_public=True)

    # 🔹 Statistiques globales
    total_cagnotte = (
        Donation.objects.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0
    )
    total_engaged_users = (
        Engagement.objects.values("user").distinct().count()
    )
    total_beneficiaries = (
        Beneficiary.objects.filter(is_active=True).count()
    )
    total_regions = (
        Beneficiary.objects.filter(is_active=True)
        .values('region').distinct().count()
    )

    # 🔹 Derniers engagements (5 plus récents)
    derniers_engagements = (
        Engagement.objects.select_related("user")
        .order_by("-date")[:5]
    )

    # 🔹 Progression cagnotte globale (si tu as un objectif global, sinon retire)
    total_goal = Project.objects.aggregate(goal=Sum("goal_amount"))["goal"] or 0
    progress_percentage = round((total_cagnotte / total_goal) * 100, 2) if total_goal else 0

    context = {
        "projects": projects,
        "publications": publications,
        "total_projects": total_projects,
        "total_cagnotte": total_cagnotte,
        "total_beneficiaries": total_beneficiaries,
        "total_engaged_users": total_engaged_users,
        "total_regions": total_regions,
        "derniers_engagements": derniers_engagements,
        "total_goal": total_goal,
        "progress_percentage": progress_percentage,
    }

    return render(request, "social/soci_index.html", context)
