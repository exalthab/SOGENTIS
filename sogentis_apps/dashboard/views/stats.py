# dashboard/views/stats.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import StatCard, breadcrumb


@login_required
def stats_view(request):
    cards = []

    # Notes
    try:
        from dashboard.models.dashboard_note import DashboardNote
        cards.append(StatCard(label=_("Notes"), value=DashboardNote.objects.filter(author=request.user).count(), icon="📝"))
    except Exception:
        pass

    # Donations (si dispo)
    try:
        from donations.models import Donation  # ajuste si ton app est ailleurs
        cards.append(StatCard(label=_("Dons"), value=Donation.objects.filter(user=request.user).count(), icon="💝"))
    except Exception:
        pass

    # Orders (si dispo)
    try:
        from economic.ecommerce.models.order import Order  # ajuste selon ton projet
        cards.append(StatCard(label=_("Commandes"), value=Order.objects.filter(user=request.user).count(), icon="🧾"))
    except Exception:
        pass

    return render(request, "dashboard/stats.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Stats"), None)),
        "cards": [c.__dict__ for c in cards],
    })






# # dashboard/views/stats.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
# from django.db.models import Sum
# from django.db.models.functions import TruncMonth

# from social.models import Donation, Engagement


# @login_required
# def stats_view(request):
#     """
#     Vue des statistiques personnelles du dashboard utilisateur.

#     Affiche notamment :
#     - le total des dons de l'utilisateur,
#     - le nombre d'engagements,
#     - des cartes résumées,
#     - des séries prêtes pour l'affichage de graphiques.
#     """
#     user = request.user

#     # =====================================================
#     # TOTAL DES DONS (avec fallback robuste)
#     # =====================================================
#     donation_total = 0

#     # Si tu as défini Donation.objects.aggregate_total_amount(user=...), on essaie d'abord
#     if hasattr(Donation.objects, "aggregate_total_amount"):
#         try:
#             donation_total = Donation.objects.aggregate_total_amount(user=user) or 0
#         except Exception:
#             donation_total = 0

#     # Fallback standard si pas de méthode custom
#     if donation_total == 0:
#         donation_total = (
#             Donation.objects.filter(user=user)
#             .aggregate(total=Sum("amount"))
#             .get("total")
#             or 0
#         )

#     # On force un float pour éviter les soucis de Decimal en JS
#     donation_total = float(donation_total)

#     # =====================================================
#     # NOMBRE D'ENGAGEMENTS
#     # =====================================================
#     engagement_count = Engagement.objects.filter(user=user).count()

#     # =====================================================
#     # CARTES RÉSUMÉ (affichées en haut)
#     # =====================================================
#     summary_cards = [
#         {
#             "label": _("Total des dons"),
#             "value": f"{donation_total:,.0f} FCFA",
#             "color": "primary",
#             "icon": "fas fa-coins",
#         },
#         {
#             "label": _("Engagements"),
#             "value": engagement_count,
#             "color": "success",
#             "icon": "fas fa-people-arrows",
#         },
#     ]

#     # =====================================================
#     # DONATIONS PAR MOIS (pour les graphiques)
#     # =====================================================
#     donations_by_month = []

#     if hasattr(Donation.objects, "get_donations_by_month"):
#         # Méthode custom sur le manager si tu l'as prévue
#         try:
#             donations_by_month = Donation.objects.get_donations_by_month(user=user)
#         except Exception:
#             donations_by_month = []
#     else:
#         # Fallback générique : groupement par mois sur created_at
#         qs = (
#             Donation.objects.filter(user=user)
#             .annotate(month=TruncMonth("created_at"))
#             .values("month")
#             .annotate(total=Sum("amount"))
#             .order_by("month")
#         )

#         donations_by_month = [
#             {
#                 "month": item["month"].strftime("%Y-%m") if item["month"] else "",
#                 "total": float(item["total"] or 0),
#             }
#             for item in qs
#         ]

#     chart_labels = [item["month"] for item in donations_by_month]
#     chart_values = [item["total"] for item in donations_by_month]

#     context = {
#         "page_title": _("Statistiques"),
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#         "chart_labels": chart_labels,
#         "chart_values": chart_values,
#     }

#     return render(request, "dashboard/stats.html", context)







# # dashboard/views/stats.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
# from social.models import Donation, Engagement


# @login_required
# def stats_view(request):
#     """
#     Vue des statistiques personnelles du dashboard utilisateur.
#     Affiche :
#     - total des dons
#     - nombre d'engagements
#     - cartes résumées
#     - prêt pour graphes et analyses avancées
#     """
#     user = request.user

#     # Total des dons —  méthode personnalisée dans Donation.objects
#     donation_total = Donation.objects.aggregate_total_amount(user=user) or 0

#     # Nombre d'engagements
#     engagement_count = Engagement.objects.filter(user=user).count()

#     # Construction des cartes affichées dans le template
#     summary_cards = [
#         {
#             "label": _("Total des dons"),
#             "value": f"{donation_total:,.2f} FCFA",
#             "color": "primary",
#             "icon": "bi-cash-coin",
#         },
#         {
#             "label": _("Engagements"),
#             "value": engagement_count,
#             "color": "success",
#             "icon": "bi-check2-circle",
#         },
#     ]

#     # 🔵 Partie extensible : graphiques mensuels (exemple)
#     donations_by_month = (
#         Donation.objects.get_donations_by_month(user=user)
#         if hasattr(Donation.objects, "get_donations_by_month")
#         else []
#     )

#     labels = [item["month"] for item in donations_by_month]
#     values = [item["total"] for item in donations_by_month]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#         "chart_labels": labels,
#         "chart_values": values,
#     }

#     return render(request, "dashboard/stats.html", context)







# #dashboard/views/stats.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
# from social.models import Donation, Engagement

# @login_required
# def dashboard_stats_view(request):
#     user = request.user

#     # Total des dons de l'utilisateur (gère None pour éviter les erreurs)
#     donation_total = Donation.objects.aggregate_total_amount(user=user) or 0

#     # Nombre d'engagements
#     engagement_count = Engagement.objects.filter(user=user).count()

#     # Construction des cartes résumées pour le template
#     summary_cards = [
#         {
#             "label": _("Total des dons"),
#             "value": f"{donation_total:,.2f} FCFA",  # Formatage 1 234,56 FCFA
#             "color": "primary"
#         },
#         {
#             "label": _("Engagements"),
#             "value": engagement_count,
#             "color": "success"
#         },
#         # Tu peux ajouter d'autres cards ici si besoin
#     ]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     }
#     return render(request, "dashboard/stats.html", context)













# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
# from social.models import Donation, Engagement

# @login_required
# def dashboard_stats_view(request):
#     user = request.user

#     # Total des dons via manager custom (None sécurisé)
#     donation_total = Donation.objects.aggregate_total_amount(user=user) or 0

#     engagement_count = Engagement.objects.filter(user=user).count()

#     # Cartes dynamiques pour affichage dans le template
#     summary_cards = [
#         {"label": _("Total des dons"), "value": f"{donation_total:.2f} FCFA", "color": "primary"},
#         {"label": _("Engagements"), "value": engagement_count, "color": "success"},
#     ]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     }
#     return render(request, "dashboard/stats.html", context)



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
