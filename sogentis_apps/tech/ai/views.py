# tech/ai/views.py
from __future__ import annotations
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

def ai_index_view(request: HttpRequest) -> HttpResponse:
    ctx = {
        "page_title": _("Tech+ — AI"),
        "seo_title": _("AI"),
        "seo_description": _("Assistants et automatisations IA."),
    }
    return render(request, "tech/ai/index.html", ctx)
