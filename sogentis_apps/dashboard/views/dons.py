# #dashboard/views/dons.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from social.models import Don

@login_required
def dashboard_dons_list_view(request):
    """
    Liste paginée des dons de l'utilisateur connecté.
    """
    dons = Don.objects.filter(user=request.user).order_by("-date")
    paginator = Paginator(dons, 10)
    page = request.GET.get("page")
    dons_page = paginator.get_page(page)
    return render(request, "dashboard/dons_list.html", {
        "dons": dons_page,
        "page_title": _("Mes dons"),
    })



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from social.models import Donation, Don
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.contrib.auth.decorators import login_required
# from django.utils.translation import gettext_lazy as _
# from social.models import Don

# @login_required
# def dashboard_dons_list_view(request):
#     dons = Don.objects.filter(user=request.user).order_by("-date")
#     paginator = Paginator(dons, 10)
#     page = request.GET.get("page")
#     dons_page = paginator.get_page(page)
#     return render(request, "dashboard/dons_list.html", {
#         "dons": dons_page,
#         "page_title": _("Mes dons"),
#     })
