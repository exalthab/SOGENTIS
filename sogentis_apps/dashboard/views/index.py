# # dashboard/views/index.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts_users.models.users_profile import UserProfile
from dashboard.services.stats_services import get_dashboard_stats, get_detailed_statistics
from social.models import Engagement, Donation, Evenement

@login_required
def dashboard_index_view(request):
    user = request.user
    profile = getattr(user, "userprofile", None)

    if not profile or profile.status != 'approved':
        messages.warning(request, _("Votre compte est en attente de validation ou a été refusé."))
        return redirect('accounts_users_web:profile_pending_notice')  # Cette vue/template doit exister

    dashboard_data = get_dashboard_stats()
    detailed_stats = get_detailed_statistics()

    derniers_engagements = Engagement.objects.filter(user=user).order_by("-date")[:5]
    derniers_dons = Donation.objects.filter(user=user).order_by("-created_at")[:5]
    prochain_evenement = Evenement.objects.filter(date__gte=timezone.now()).order_by("date").first()

    cards = [
        (_("Total des membres"), dashboard_data["stats"]["total_members"], "bi-people-fill", "primary"),
        (_("Volontaires"), dashboard_data["stats"]["total_volunteers"], "bi-person-check-fill", "success"),
        (_("Montant total des dons"), f"{dashboard_data['stats']['total_donations']:,} FCFA", "bi-cash-stack", "info"),
        (_("Projets actifs"), dashboard_data["stats"]["total_projects"], "bi-diagram-3-fill", "warning"),
        (_("Engagements"), dashboard_data["stats"]["engagements_count"], "bi-journal-check", "dark"),
        (_("Donateurs"), dashboard_data["stats"]["donors_count"], "bi-hand-thumbs-up", "secondary"),
    ]

    context = {
        "profile": profile,
        "derniers_engagements": derniers_engagements,
        "derniers_dons": derniers_dons,
        "prochain_evenement": prochain_evenement,
        "detailed_stats": detailed_stats,
        "cards": cards,
    }
    return render(request, "dashboard/index.html", context)

@login_required
def index_redirect_view(request):
    """
    Redirection vers la vue principale du dashboard.
    """
    return redirect("dashboard:index")




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def dashboard_index_view(request):
#     return render(request, "dashboard/index.html")
