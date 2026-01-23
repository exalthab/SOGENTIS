# dashboard/views/social/home.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import breadcrumb


@login_required
def social_dashboard_home_view(request):
    return render(request, "dashboard/social/home.html", {
        "page_title": _("Mon espace social"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), None)),
        "dashboard_menu": "dashboard/social/_menu.html",
    })



# # dashboard/views/social/social.py

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# @login_required
# def social_dashboard_home_view(request):
#     """
#     Dashboard Social :
#     - Donateur
#     - Membre
#     - Volontaire
#     - Institution
#     """
#     return render(
#         request,
#         "dashboard/social/home.html",
#         {
#             "page_title": _("Mon espace social"),
#             "dashboard_menu": "dashboard/social/_menu.html",
#             # "section_menu": "core/partials/_menu_dashboard.html",
#         }
#     )    
