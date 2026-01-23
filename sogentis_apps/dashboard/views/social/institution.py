# dashboard/views/social/institution.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.access import require_social_role
from dashboard.views.utils import breadcrumb

@require_social_role("INSTITUTION")
def institution_home_view(request):
    return render(request, "dashboard/social/institution/home.html", {
        "page_title": _("Institution"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), "/dashboard/social/"), (_("Institution"), None)),
    })





# # dashboard/views/social/institution.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
# from dashboard.views.utils import breadcrumb

# @login_required
# def institution_home_view(request):
#     return render(request, "dashboard/social/institution/home.html", {
#         "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), "/dashboard/social/"), (_("Institution"), None)),
#     })





# # dashboard/views/social/institution.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render


# @login_required
# def institution_home_view(request):
#     return render(request, "dashboard/social/institution/home.html")
