# # dashboard/views/dashboard.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts_users.models.users_profile import UserProfile
from dashboard.services.stats_services import get_dashboard_stats
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

@login_required
def dashboard_index_view(request):
    user = request.user
    profile = getattr(user, "userprofile", None)

    # Vérification du statut du profil utilisateur
    if not profile or profile.status != 'approved':
        messages.warning(request, _("Votre profil est en attente de validation ou a été refusé."))
        return redirect('accounts_users_web:profile_pending_notice')  # Cette vue/template doit exister

    # Récupération des données statistiques du dashboard (statistiques personnalisées par utilisateur)
    dashboard_data = get_dashboard_stats(user)

    context = {
        "profile": profile,
        **dashboard_data,
    }
    return render(request, "dashboard/index.html", context)




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from accounts_users.models.users_profile import UserProfile
# from dashboard.services.stats_services import get_dashboard_stats
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _

# @login_required
# def dashboard_index_view(request):
#     user = request.user
#     profile = getattr(user, "userprofile", None)

#     # Vérification du statut du profil utilisateur
#     if not profile or profile.status != 'approved':
#         messages.warning(request, _("Votre profil est en attente de validation ou a été refusé."))
#         return redirect('accounts_users_web:profile_pending_notice')  # Cette vue doit exister

#     # Récupération des données statistiques du dashboard
#     dashboard_data = get_dashboard_stats(user)

#     context = {
#         "profile": profile,
#         **dashboard_data,
#     }
#     return render(request, "dashboard/index.html", context)




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from social.models import Donation, Engagement
# from accounts_users.models.users_profile import UserProfile


# @login_required
# def dashboard_index_view(request):
#     user = request.user
#     profile = getattr(user, "userprofile", None)
#     donations = Donation.objects.filter(user=user)
#     engagements = Engagement.objects.filter(user=user)

#     context = {
#         "profile": profile,
#         "donations": donations,
#         "engagements": engagements,
#     }
#     return render(request, "dashboard/index.html", context)
