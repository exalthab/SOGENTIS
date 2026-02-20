# tech/labs/views.py
from __future__ import annotations
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

def labs_index_view(request: HttpRequest) -> HttpResponse:
    ctx = {
        "page_title": _("Tech+ — Labs"),
        "seo_title": _("Labs"),
        "seo_description": _("POC et modules expérimentaux."),
    }
    return render(request, "tech/labs/index.html", ctx)
