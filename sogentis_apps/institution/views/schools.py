from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def schools_home_view(request):
    context = {
        "page_title": _("Écoles & Formation"),
    }
    return render(request, "institution/schools.html", context)
