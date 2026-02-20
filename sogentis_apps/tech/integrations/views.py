# tech/integrations/views.py
from __future__ import annotations
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

def integrations_index_view(request: HttpRequest) -> HttpResponse:
    ctx = {
        "page_title": _("Tech+ — Intégrations"),
        "seo_title": _("Intégrations"),
        "seo_description": _("Connecteurs, webhooks et services externes."),
    }
    return render(request, "tech/integrations/index.html", ctx)
