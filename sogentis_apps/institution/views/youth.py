from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def youth_home_view(request):
    context = {
        "page_title": _("Jeunesse & Récréation"),
    }
    return render(request, "institution/youth.html", context)
