# tech/analytics/views.py
from __future__ import annotations
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

def analytics_index_view(request: HttpRequest) -> HttpResponse:
    ctx = {
        "page_title": _("Tech+ — Analytics"),
        "seo_title": _("Analytics"),
        "seo_description": _("KPI et reporting cross-modules."),
    }
    return render(request, "tech/analytics/index.html", ctx)
