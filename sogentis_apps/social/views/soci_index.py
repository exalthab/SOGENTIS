# social/views/soci_index.py
from __future__ import annotations

from django.core.cache import cache
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.shortcuts import render

from social.models import Publication, Project, Donation, Engagement
from stakeholders.models.beneficiaries import Beneficiary


def _has_field(model, field_name: str) -> bool:
    return any(getattr(f, "name", None) == field_name for f in model._meta.get_fields())


def soci_index_view(request):
    """
    Page d’accueil Social.
    - Projets actifs
    - Publications publiques
    - Stats globales
    - Derniers engagements
    """

    # =========================================================
    # 0) Cache (optionnel)
    # =========================================================
    cache_key = "social:soci_index:stats:v1"
    cached = cache.get(cache_key)
    if cached:
        return render(request, "social/soci_index.html", cached)

    # =========================================================
    # 1) Projets actifs
    # =========================================================
    projects = Project.objects.filter(is_active=True)
    total_projects = projects.count()

    # =========================================================
    # 2) Publications publiques
    # =========================================================
    publications = Publication.objects.filter(is_public=True).order_by("-pk")

    # =========================================================
    # 3) Stats globales
    # =========================================================
    # Total cagnotte (donations payées)
    total_cagnotte = (
        Donation.objects.filter(status="paid")
        .aggregate(total=Coalesce(Sum("amount"), 0))
        .get("total", 0)
    )

    # Utilisateurs engagés (distinct)
    total_engaged_users = (
        Engagement.objects.aggregate(cnt=Coalesce(Count("user", distinct=True), 0))
        .get("cnt", 0)
    )

    # Bénéficiaires actifs
    total_beneficiaries = Beneficiary.objects.filter(is_active=True).count()

    # Régions couvertes (ignore null/empty)
    total_regions = (
        Beneficiary.objects.filter(is_active=True)
        .exclude(region__isnull=True)
        .exclude(region__exact="")
        .values_list("region", flat=True)
        .distinct()
        .count()
    )

    # =========================================================
    # 4) Derniers engagements
    # =========================================================
    # On choisit un champ d’ordre robuste (date / created_at / created / pk)
    if _has_field(Engagement, "date"):
        order_field = "-date"
    elif _has_field(Engagement, "created_at"):
        order_field = "-created_at"
    elif _has_field(Engagement, "created"):
        order_field = "-created"
    else:
        order_field = "-pk"

    derniers_engagements = (
        Engagement.objects.select_related("user")
        .order_by(order_field)[:5]
    )

    # =========================================================
    # 5) Objectif global + progression
    # =========================================================
    # Ton template utilise project.goal ; ton ancien code utilisait goal_amount.
    # On supporte les deux au cas où.
    goal_field = None
    if _has_field(Project, "goal"):
        goal_field = "goal"
    elif _has_field(Project, "goal_amount"):
        goal_field = "goal_amount"

    if goal_field:
        total_goal = Project.objects.aggregate(goal=Coalesce(Sum(goal_field), 0)).get("goal", 0)
    else:
        total_goal = 0

    progress_percentage = round((float(total_cagnotte) / float(total_goal)) * 100, 2) if total_goal else 0

    # =========================================================
    # 6) Context (compat template)
    # =========================================================
    context = {
        "projects": projects,
        "publications": publications,

        "total_projects": total_projects,
        "total_cagnotte": total_cagnotte,

        # Ton template utilise les 2 noms -> on fournit les 2
        "total_beneficiaries": total_beneficiaries,
        "total_beneficiaires": total_beneficiaries,

        "total_engaged_users": total_engaged_users,
        "total_regions": total_regions,

        "derniers_engagements": derniers_engagements,
        "total_goal": total_goal,
        "progress_percentage": progress_percentage,
    }

    # Cache léger (5 minutes). Mets 0 pour désactiver.
    cache.set(cache_key, context, timeout=300)

    return render(request, "social/soci_index.html", context)








# # social/views/soci_index.py

# from django.shortcuts import render
# from django.db.models import Sum
# from social.models import Publication, Project, Donation, Engagement
# from stakeholders.models.beneficiaries import Beneficiary

# def soci_index_view(request):
#     # 🔹 Projets actifs
#     projects = Project.objects.filter(is_active=True)
#     total_projects = projects.count()

#     # 🔹 Publications publiques
#     publications = Publication.objects.filter(is_public=True)

#     # 🔹 Statistiques globales
#     total_cagnotte = (
#         Donation.objects.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0
#     )
#     total_engaged_users = (
#         Engagement.objects.values("user").distinct().count()
#     )
#     total_beneficiaries = (
#         Beneficiary.objects.filter(is_active=True).count()
#     )
#     total_regions = (
#         Beneficiary.objects.filter(is_active=True)
#         .values('region').distinct().count()
#     )

#     # 🔹 Derniers engagements (5 plus récents)
#     derniers_engagements = (
#         Engagement.objects.select_related("user")
#         .order_by("-date")[:5]
#     )

#     # 🔹 Progression cagnotte globale (si tu as un objectif global, sinon retire)
#     total_goal = Project.objects.aggregate(goal=Sum("goal_amount"))["goal"] or 0
#     progress_percentage = round((total_cagnotte / total_goal) * 100, 2) if total_goal else 0

#     context = {
#         "projects": projects,
#         "publications": publications,
#         "total_projects": total_projects,
#         "total_cagnotte": total_cagnotte,
#         "total_beneficiaries": total_beneficiaries,
#         "total_engaged_users": total_engaged_users,
#         "total_regions": total_regions,
#         "derniers_engagements": derniers_engagements,
#         "total_goal": total_goal,
#         "progress_percentage": progress_percentage,
#     }

#     return render(request, "social/soci_index.html", context)
