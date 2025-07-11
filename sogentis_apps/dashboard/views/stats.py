# #dashboard/views/stats.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from social.models import Donation, Engagement

@login_required
def dashboard_stats_view(request):
    user = request.user

    # Total des dons via manager custom (None sécurisé)
    donation_total = Donation.objects.aggregate_total_amount(user=user) or 0

    engagement_count = Engagement.objects.filter(user=user).count()

    # Cartes dynamiques pour affichage dans le template
    summary_cards = [
        {"label": _("Total des dons"), "value": f"{donation_total:.2f} FCFA", "color": "primary"},
        {"label": _("Engagements"), "value": engagement_count, "color": "success"},
    ]

    context = {
        "donation_total": donation_total,
        "engagement_count": engagement_count,
        "summary_cards": summary_cards,
    }
    return render(request, "dashboard/stats.html", context)



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def dashboard_stats_view(request):
#     # Ajoute ici la récupération de stats réelles
#     stats = {
#         "nb_notes": request.user.dashboard_notes.count(),
#         # autres stats à ajouter
#     }
#     return render(request, "dashboard/stats.html", {"stats": stats})
