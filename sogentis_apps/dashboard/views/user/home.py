# dashboard/views/user/home.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import StatCard, breadcrumb


@login_required
def user_dashboard_home_view(request):
    cards = []

    # commandes si dispo
    orders = []
    try:
        from economic.ecommerce.models.order import Order
        orders = Order.objects.filter(user=request.user).order_by("-created_at")[:8]
        cards.append(StatCard(label=_("Commandes"), value=Order.objects.filter(user=request.user).count(), icon="🧾"))
    except Exception:
        orders = []

    return render(request, "dashboard/user/home.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Utilisateur"), None)),
        "cards": [c.__dict__ for c in cards],
        "orders": orders,
    })




# # dashboard/views/user/home.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# @login_required
# def user_dashboard_home_view(request):
#     user = request.user

#     # -------------------------------------------------
#     # Statut / adhésion utilisateur (fallback propre)
#     # -------------------------------------------------
#     membership_label = getattr(user, "membership_status_label", None)

#     if membership_label is None:
#         # Tentative de passer par un profil, si présent
#         try:
#             profile = user.profile  # adapte si ton related_name est différent
#             membership_label = getattr(
#                 profile,
#                 "membership_status_label",
#                 None,
#             ) or str(profile)
#         except Exception:
#             membership_label = _("Standard")

#     # -------------------------------------------------
#     # Statistiques de base (commandes, dons, notes)
#     # On met des valeurs par défaut sûres,
#     # et on n'importe que DashboardNote pour éviter les erreurs.
#     # -------------------------------------------------
#     user_orders_count = 0
#     user_donations_count = 0
#     user_notes_count = 0
#     last_notes = []

#     try:
#         # On sait que ce modèle existe dans ton projet (notes dashboard)
#         from dashboard.models.dashboard_note import DashboardNote

#         notes_qs = (
#             DashboardNote.objects.filter(user=user)
#             .order_by("-updated_at", "-created_at")
#         )
#         user_notes_count = notes_qs.count()
#         last_notes = list(notes_qs[:5])
#     except Exception:
#         # Si le modèle n’est pas encore migré, on ne casse pas la vue
#         pass

#     context = {
#         "page_title": _("Mon espace utilisateur"),
#         "dashboard_menu": "dashboard/user/_menu.html",

#         # Pour le template dashboard/user/home.html
#         "user_membership_status": membership_label,
#         "user_orders_count": user_orders_count,
#         "user_donations_count": user_donations_count,
#         "user_notes_count": user_notes_count,
#         "last_notes": last_notes,
#     }

#     return render(request, "dashboard/user/home.html", context)








# # dashboard/views/user/home.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# @login_required
# def user_dashboard_home_view(request):
#     return render(
#         request,
#         "dashboard/user/home.html",
#         {
#             "page_title": _("Mon espace utilisateur"),
#             # "section_menu": "core/partials/_menu_dashboard.html",
#             "dashboard_menu": "dashboard/user/_menu.html",

#         }
#     )









# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def user_dashboard_view(request):
#     return render(request, "dashboard/user/home.html", {
#         "page_title": "Dashboard utilisateur",
#     })
