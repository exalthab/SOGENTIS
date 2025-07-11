# # dashboard/views/engagements.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from social.models import Engagement

@login_required
def dashboard_engagements_list_view(request):
    """
    Affiche la liste paginée (ou complète) des engagements de l'utilisateur connecté,
    triés du plus récent au plus ancien.
    """
    engagements = Engagement.objects.filter(user=request.user).order_by("-date")
    context = {
        "engagements": engagements,
        "page_title": _("Mes engagements"),
    }
    return render(request, "dashboard/engagements_list.html", context)




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from social.models import Engagement

# @login_required
# def dashboard_engagements_list_view(request):
#     # Tri des engagements par date décroissante (les plus récents en premier)
#     engagements = Engagement.objects.filter(user=request.user).order_by("-date")
#     return render(request, "dashboard/engagements_list.html", {"engagements": engagements})

