# #dashboard/views/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum

from social.models import Don, Engagement

def home(request):
    """
    Page d'accueil du tableau de bord (publique ou protégée selon le design).
    """
    return render(request, "dashboard/home.html")

# Vue principale du dashboard déplacée vers index.py (voir dashboard/views/index.py)

@login_required
def dashboard_stats_view(request):
    """
    Statistiques globales de l'utilisateur (total dons, engagements…)
    """
    user = request.user

    # Agrégation du total des dons (compatible manager custom ou fallback)
    if hasattr(Don.objects, "aggregate_total_amount"):
        donation_total = Don.objects.filter(user=user).aggregate_total_amount()
    else:
        donation_total = Don.objects.filter(user=user).aggregate(total=Sum("montant"))["total"]

    engagement_count = Engagement.objects.filter(user=user).count()

    summary_cards = [
        {"label": _("Total des dons"), "value": f"{donation_total or 0} FCFA", "color": "primary"},
        {"label": _("Engagements"),    "value": engagement_count,              "color": "success"},
    ]

    context = {
        "donation_total": donation_total,
        "engagement_count": engagement_count,
        "summary_cards": summary_cards,
    }
    return render(request, "dashboard/stats.html", context)

@login_required
def engagements_list_view(request):
    """
    Liste paginée des engagements de l'utilisateur connecté.
    """
    engagements = Engagement.objects.filter(user=request.user).order_by("-created_at", "-date")
    paginator = Paginator(engagements, 10)
    page_number = request.GET.get("page")
    engagements_page = paginator.get_page(page_number)

    return render(request, "dashboard/engagements_list.html", {
        "engagements": engagements_page,
        "page_title": _("Mes engagements"),
    })

@login_required
def dons_list_view(request):
    """
    Liste paginée des dons de l'utilisateur connecté.
    """
    dons = Don.objects.filter(user=request.user).order_by("-date")
    paginator = Paginator(dons, 10)
    page_number = request.GET.get("page")
    dons_page = paginator.get_page(page_number)

    return render(request, "dashboard/dons_list.html", {
        "dons": dons_page,
        "page_title": _("Mes dons"),
    })




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _
# from django.db.models import Sum

# from social.models import Don, Engagement  # Utilisation cohérente des modèles Don et Engagement

# def home(request):
#     """
#     Page d'accueil du tableau de bord (publique ou protégée selon le design).
#     """
#     return render(request, "dashboard/home.html")

# # Vue principale du tableau de bord déplacée vers index.py pour éviter les conflits de nom.
# # (voir dashboard/views/index.py pour la fonction dashboard_index_view)

# @login_required
# def dashboard_stats_view(request):
#     """
#     Vue affichant les statistiques globales de l'utilisateur (total des dons, engagements, etc.).
#     """
#     user = request.user

#     # Vérifie si la méthode d’agrégation personnalisée existe sur le manager Don.objects
#     if hasattr(Don.objects, "aggregate_total_amount"):
#         donation_total = Don.objects.filter(user=user).aggregate_total_amount()
#     else:
#         # Solution de repli : somme des montants des dons de l'utilisateur
#         donation_total = Don.objects.filter(user=user).aggregate(total=Sum("amount"))["total"]

#     engagement_count = Engagement.objects.filter(user=user).count()

#     # Prépare les données pour les cartes de synthèse affichées dans le template
#     summary_cards = [
#         {"label": "Total des dons", "value": f"{donation_total or 0} €", "color": "primary"},
#         {"label": "Engagements",    "value": engagement_count,          "color": "success"},
#     ]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     }
#     return render(request, "dashboard/stats.html", context)

# @login_required
# def engagements_list_view(request):
#     """
#     Liste paginée des engagements de l'utilisateur connecté.
#     """
#     engagements = Engagement.objects.filter(user=request.user).order_by("-created_at")
#     paginator = Paginator(engagements, 10)
#     page_number = request.GET.get("page")
#     engagements_page = paginator.get_page(page_number)

#     return render(request, "dashboard/engagements_list.html", {
#         "engagements": engagements_page,
#         "page_title": _("Mes engagements"),
#     })

# @login_required
# def dons_list_view(request):
#     """
#     Liste paginée des dons de l'utilisateur connecté.
#     """
#     dons = Don.objects.filter(user=request.user).order_by("-date")
#     paginator = Paginator(dons, 10)
#     page_number = request.GET.get("page")
#     dons_page = paginator.get_page(page_number)

#     return render(request, "dashboard/dons_list.html", {
#         "dons": dons_page,
#         "page_title": _("Mes dons"),
#     })
