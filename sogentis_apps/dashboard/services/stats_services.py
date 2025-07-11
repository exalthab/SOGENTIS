# dashboard/services/stats_services.py
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear
from social.models import Donation, Engagement, Project
from accounts_users.models.users_profile import UserProfile

def get_dashboard_stats(user=None):
    """
    Statistiques personnalisées pour l'utilisateur connecté OU globales si user=None.
    """
    # Comptes de membres et volontaires par code rôle
    total_members = UserProfile.objects.filter(membership_role__code="MEMBER").count()
    total_volunteers = UserProfile.objects.filter(membership_role__code="VOLUNTEER").count()
    total_projects = Project.objects.filter(is_active=True).count()
    total_donations = Donation.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] if user else Donation.objects.aggregate(total=Sum("amount"))["total"]
    total_donations = total_donations or 0
    engagements_count = Engagement.objects.filter(user=user).count() if user else Engagement.objects.count()
    # Comptage distincts (email + user) pour bien gérer donateurs connectés et non-connectés
    donors_count = Donation.objects.exclude(email="").values("email").distinct().count() + Donation.objects.filter(user__isnull=False).values("user").distinct().count()

    return {
        "total_members": total_members,
        "total_volunteers": total_volunteers,
        "total_donations": total_donations,
        "total_projects": total_projects,
        "engagements_count": engagements_count,
        "donors_count": donors_count,
    }

def get_detailed_statistics():
    """
    Statistiques globales détaillées : dons par projet, engagements par année.
    """
    donations_by_project = (
        Donation.objects
        .filter(project__isnull=False)
        .values("project__title")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    engagements_by_year = (
        Engagement.objects
        .annotate(year=ExtractYear("date"))
        .values("year")
        .annotate(count=Count("id"))
        .order_by("year")
    )

    return {
        "donations_by_project": list(donations_by_project),
        "engagements_by_year": list(engagements_by_year),
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

