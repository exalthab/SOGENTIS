# dashboard/views/social/beneficiary.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from dashboard.views.utils import breadcrumb

@login_required
def beneficiary_home_view(request):
    return render(request, "dashboard/social/beneficiary/home.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), "/dashboard/social/"), (_("Bénéficiaire"), None)),
    })




# # dashboard/views/social/beneficiary.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render


# @login_required
# def beneficiary_home_view(request):
#     return render(request, "dashboard/social/beneficiary/home.html")
