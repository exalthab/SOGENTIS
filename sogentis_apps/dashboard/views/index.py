from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts_users.models.users_profile import UserProfile
from dashboard.services.stats_services import get_dashboard_stats, get_detailed_statistics
from social.models import Engagement, Donation, Evenement

import json

@login_required
def dashboard_index_view(request):
    user = request.user

    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = None

    if not profile or profile.status != 'approved':
        messages.warning(request, _("Votre compte est en attente de validation ou a été refusé."))
        return redirect('accounts_users_web:profile_pending_notice')

    # Statistiques globales et détaillées
    dashboard_data = get_dashboard_stats()
    detailed_stats = get_detailed_statistics(user=user)

    # Données dynamiques récentes
    derniers_engagements = Engagement.objects.filter(user=user).order_by("-date")[:5]
    derniers_dons = Donation.objects.filter(user=user).order_by("-created_at")[:5]
    prochain_evenement = (
        Evenement.objects.filter(date__gte=timezone.now())
        .order_by("date")
        .first()
    )

    stats = dashboard_data.get("stats", {})
    cards = [
        {"label": _("Total des membres"), "value": stats.get("total_members", 0), "icon": "bi-people-fill", "color": "primary"},
        {"label": _("Volontaires"), "value": stats.get("total_volunteers", 0), "icon": "bi-person-check-fill", "color": "success"},
        {"label": _("Montant total des dons"), "value": f"{stats.get('total_donations', 0):,} FCFA", "icon": "bi-cash-stack", "color": "info"},
        {"label": _("Projets actifs"), "value": stats.get("total_projects", 0), "icon": "bi-diagram-3-fill", "color": "warning"},
        {"label": _("Engagements"), "value": stats.get("engagements_count", 0), "icon": "bi-journal-check", "color": "dark"},
        {"label": _("Donateurs"), "value": stats.get("donors_count", 0), "icon": "bi-hand-thumbs-up", "color": "secondary"},
    ]

    # Exemple visiteurs (statique, remplace par tes données dynamiques pays)
    visitors_locations = [
        {"country": "Sénégal", "percent": 55, "lat": 14.5, "lon": -14.5},
        {"country": "France", "percent": 20, "lat": 46.603354, "lon": 1.888334},
        {"country": "Côte d'Ivoire", "percent": 10, "lat": 7.54, "lon": -5.5471},
        {"country": "États-Unis", "percent": 8, "lat": 37.0902, "lon": -95.7129},
        {"country": "Maroc", "percent": 7, "lat": 31.7917, "lon": -7.0926},
    ]

    # To do + météo exemple (dynamise à volonté)
    todos = [
        {"label": "Contacter nouveau donateur", "done": True},
        {"label": "Publier un témoignage", "done": False},
    ]
    weather = {
        "location": "Dakar",
        "time": "Vendredi, 14:30",
        "status": "Soleil voilé"
    }

    # Activités récentes
    recent_activities = [
        f"Nouvel engagement par {e.user.get_full_name() or e.user.username} le {e.date.strftime('%d/%m/%Y')}"
        for e in derniers_engagements
    ] + [
        f"Don effectué par {d.user.get_full_name() or d.user.username} le {d.created_at.strftime('%d/%m/%Y')}"
        for d in derniers_dons
    ]

    context = {
        "profile": profile,
        "detailed_stats": detailed_stats,
        "derniers_engagements": derniers_engagements,
        "derniers_dons": derniers_dons,
        "prochain_evenement": prochain_evenement,
        "cards": cards,
        "chart_labels": json.dumps(detailed_stats.get("donations_by_month_labels", []), ensure_ascii=False),
        "chart_data": json.dumps(detailed_stats.get("donations_by_month_values", []), ensure_ascii=False),
        "recent_activities": recent_activities,
        "visitors_locations": visitors_locations,
        "todos": todos,
        "weather": weather,
        "network_labels": json.dumps(["Jan 01", "Jan 02", "Jan 03", "Jan 04", "Jan 05", "Jan 06"]),
        "network_data": json.dumps([120, 170, 250, 210, 320, 300]),
        "app_versions_labels": json.dumps(["1.0.0", "1.1.0", "2.0.0", "2.1.0"]),
        "app_versions_data": json.dumps([80, 45, 30, 10]),
        "device_labels": json.dumps(["Android", "iOS", "Web", "Autres"]),
        "device_data": json.dumps([60, 30, 7, 3]),
    }

    return render(request, "dashboard/index.html", context)


@login_required
def index_redirect_view(request):
    """ Redirection vers le dashboard """
    return redirect("dashboard:index")
