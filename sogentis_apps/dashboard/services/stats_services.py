from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear
from social.models import Donation, Engagement, Project
from accounts_users.models.users_economic_profile import UserProfile

def get_dashboard_stats(user=None):
    """
    Statistiques personnalisées pour l'utilisateur connecté OU globales si user=None.
    """
    total_members = UserProfile.objects.filter(membership_role__code="MEMBER").count()
    total_volunteers = UserProfile.objects.filter(membership_role__code="VOLUNTEER").count()
    total_projects = Project.objects.filter(is_active=True).count()
    if user:
        total_donations = Donation.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] or 0
        engagements_count = Engagement.objects.filter(user=user).count()
    else:
        total_donations = Donation.objects.aggregate(total=Sum("amount"))["total"] or 0
        engagements_count = Engagement.objects.count()

    # Donateurs distincts (par email + par user authentifié)
    donors_count = (
        Donation.objects.exclude(email="").values("email").distinct().count()
        + Donation.objects.filter(user__isnull=False).values("user").distinct().count()
    )

    return {
        "total_members": total_members,
        "total_volunteers": total_volunteers,
        "total_donations": total_donations,
        "total_projects": total_projects,
        "engagements_count": engagements_count,
        "donors_count": donors_count,
    }

def get_detailed_statistics(user=None):
    """
    Statistiques détaillées : 
    - dons par projet
    - engagements par année
    Si user != None, filtre par utilisateur.
    """
    donation_qs = Donation.objects.filter(project__isnull=False)
    engagement_qs = Engagement.objects.all()

    if user:
        donation_qs = donation_qs.filter(user=user)
        engagement_qs = engagement_qs.filter(user=user)

    donations_by_project = (
        donation_qs
        .values("project__title")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    engagements_by_year = (
        engagement_qs
        .annotate(year=ExtractYear("date"))
        .values("year")
        .annotate(count=Count("id"))
        .order_by("year")
    )

    # Pour affichage graphique : labels et data séparés
    donations_by_project_labels = [x["project__title"] for x in donations_by_project]
    donations_by_project_totals = [x["total"] or 0 for x in donations_by_project]
    engagements_by_year_labels = [x["year"] for x in engagements_by_year]
    engagements_by_year_values = [x["count"] for x in engagements_by_year]

    return {
        "donations_by_project": list(donations_by_project),
        "engagements_by_year": list(engagements_by_year),
        "donations_by_project_labels": donations_by_project_labels,
        "donations_by_project_totals": donations_by_project_totals,
        "engagements_by_year_labels": engagements_by_year_labels,
        "engagements_by_year_values": engagements_by_year_values,
    }




# from django.db.models import Count, Sum
# from django.db.models.functions import ExtractYear
# from social.models import Donation, Engagement, Project
# from accounts_users.models.users_profile import UserProfile

# def get_dashboard_stats(user):
#     """
#     Statistiques personnalisées pour un utilisateur connecté.
#     """
#     return {
#         "total_members": UserProfile.objects.filter(membership_role__code="MEMBER").count(),
#         "total_volunteers": UserProfile.objects.filter(membership_role__code="VOLUNTEER").count(),
#         "total_donations": Donation.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] or 0,
#         "total_projects": Project.objects.filter(is_active=True).count(),
#         "engagements_count": Engagement.objects.filter(user=user).count(),
#         "donors_count": Donation.objects.values("user").distinct().count(),
#     }

# def get_detailed_statistics():
#     """
#     Statistiques globales détaillées (admin, exports...).
#     """
#     return {
#         "donations_by_project": Donation.objects.values("project__title")
#             .annotate(total=Sum("amount"))
#             .order_by("-total"),

#         "engagements_by_year": Engagement.objects.annotate(
#             year=ExtractYear("date")
#         ).values("year").annotate(count=Count("id")).order_by("-year"),
#     }






# def get_user_stats(user):
#     # Exemple statique, à remplacer par ta logique métier réelle
#     return {
#         "posts_count": 42,
#         "comments_count": 128,
#         "last_login": user.last_login,
#     }

