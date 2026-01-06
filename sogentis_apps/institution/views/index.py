from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def institution_home_view(request):
    context = {
        "page_title": _("Pôle Institutionnel / Local"),
    }
    return render(request, "institution/index.html", context)
