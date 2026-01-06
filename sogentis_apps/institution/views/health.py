from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def health_home_view(request):
    context = {
        "page_title": _("Santé & Centres"),
    }
    return render(request, "institution/health.html", context)
