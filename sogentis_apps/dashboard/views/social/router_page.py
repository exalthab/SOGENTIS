# dashboard/views/social/router_page.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import breadcrumb


@login_required
def social_router_page_view(request):
    return render(request, "dashboard/social/router.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), None)),
    })
