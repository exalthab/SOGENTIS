# # dashboard/utils.py
from django.db.models import Sum, Count, F
from social.models import Donation, Engagement, Project
from accounts_users.models.users_profile import UserProfile
from accounts_users.models import CustomUser

def get_dashboard_stats():
    total_members = CustomUser.objects.count()

    # Attention à la casse et au pluriel
    total_volunteers = UserProfile.objects.filter(membership_role__name__icontains="volontaire").count()

    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    donors_count = Donation.objects.exclude(email="").values('email').distinct().count()

    total_projects = Project.objects.filter(is_active=True).count()
    engagements_count = Engagement.objects.count()

    # Statistiques par projet (en évitant None pour project)
    donations_by_project = (
        Donation.objects
        .filter(project__isnull=False)
        .values(project_title=F('project__title'))
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Statistiques par année d'engagement (utilisation de TruncYear pour Django >= 1.10)
    from django.db.models.functions import ExtractYear
    engagements_by_year = (
        Engagement.objects
        .annotate(year=ExtractYear('date'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

    # Cartes de synthèse pour le dashboard (icônes Bootstrap)
    cards = [
        ("Utilisateurs", total_members, "bi-people", "primary"),
        ("Volontaires", total_volunteers, "bi-person-check", "success"),
        ("Dons (FCFA)", total_donations, "bi-cash-coin", "warning"),
        ("Projets actifs", total_projects, "bi-diagram-3", "info"),
        ("Engagements", engagements_count, "bi-calendar-check", "secondary"),
        ("Donateurs", donors_count, "bi-person-heart", "dark"),
    ]

    return {
        "cards": cards,
        "stats": {
            "total_members": total_members,
            "total_volunteers": total_volunteers,
            "total_donations": total_donations,
            "total_projects": total_projects,
            "engagements_count": engagements_count,
            "donors_count": donors_count,
        },
        "detailed_stats": {
            "donations_by_project": list(donations_by_project),
            "engagements_by_year": list(engagements_by_year),
        }
    }





# from django.db.models import Sum, Count
# from social.models import Donation, Engagement, Project
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models import CustomUser


# def get_dashboard_stats():
#     total_members = CustomUser.objects.count()

#     # ✅ Assure-toi que MembershipRole a un champ 'name'
#     total_volunteers = UserProfile.objects.filter(membership_role__name__icontains="volontaire").count()

#     total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
#     donors_count = Donation.objects.values('email').distinct().count()

#     total_projects = Project.objects.filter(is_active=True).count()
#     engagements_count = Engagement.objects.count()

#     # ✅ Correction ici : project__title
#     donations_by_project = Donation.objects.values('project__title').annotate(total=Sum('amount')).order_by('-total')

#     # ✅ Correction ici : EXTRACT(year FROM date)
#     engagements_by_year = Engagement.objects.extra(select={
#         'year': "EXTRACT(year FROM date)"
#     }).values('year').annotate(count=Count('id')).order_by('year')

#     # ✅ Cartes pour affichage
#     cards = [
#         ("Utilisateurs", total_members, "bi-people", "primary"),
#         ("Volontaires", total_volunteers, "bi-person-check", "success"),
#         ("Dons (FCFA)", total_donations, "bi-cash-coin", "warning"),
#         ("Projets actifs", total_projects, "bi-diagram-3", "info"),
#         ("Engagements", engagements_count, "bi-calendar-check", "secondary"),
#         ("Donateurs", donors_count, "bi-person-heart", "dark"),
#     ]

#     return {
#         "cards": cards,
#         "stats": {
#             "total_members": total_members,
#             "total_volunteers": total_volunteers,
#             "total_donations": total_donations,
#             "total_projects": total_projects,
#             "engagements_count": engagements_count,
#             "donors_count": donors_count,
#         },
#         "detailed_stats": {
#             "donations_by_project": list(donations_by_project),
#             "engagements_by_year": list(engagements_by_year),
#         }
#     }
