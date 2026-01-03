# dashboard/views/social/member.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from dashboard.views.utils import breadcrumb

@login_required
def member_home_view(request):
    return render(request, "dashboard/social/member/home.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), "/dashboard/social/"), (_("Membre"), None)),
    })





# # dashboard/views/social/member.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render


# @login_required
# def member_home_view(request):
#     return render(request, "dashboard/social/member/home.html")
