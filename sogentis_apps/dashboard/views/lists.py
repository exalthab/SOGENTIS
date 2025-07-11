# # dashboard/views/lists.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from social.models import Donation, Engagement

@login_required
def dashboard_lists_view(request):
    user = request.user
    donations = Donation.objects.filter(user=user).order_by("-created_at")  # ou .filter(author=user) selon modèle
    engagements = Engagement.objects.filter(user=user).order_by("-date")

    context = {
        "donations": donations,
        "engagements": engagements,
    }
    return render(request, "dashboard/lists.html", context)




# from .dons import dashboard_dons_list_view
# from .engagements import dashboard_engagements_list_view
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from social.models import Donation, Engagement
# from accounts_users.models.users_profile import UserProfile

# @login_required
# def dashboard_lists_view(request):
#     user = request.user
#     donations = Donation.objects.filter(user=user).order_by("-created_at")
#     engagements = Engagement.objects.filter(user=user).order_by("-date")

#     context = {
#         "donations": donations,
#         "engagements": engagements,
#     }
#     return render(request, "dashboard/lists.html", context)
