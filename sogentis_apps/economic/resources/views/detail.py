# economic/resources/views/detail.py
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _

from ..models import ResourceMod


def resource_detail_view(request, slug: str):
    """
    Détail d’une ressource publiée
    """
    resource = get_object_or_404(
        ResourceMod.objects.select_related("category"),
        slug=slug,
        is_published=True,  # ✅ correct
    )

    context = {
        "page_title": resource.safe_translation_getter("title", any_language=True),
        "resource": resource,
    }
    return render(request, "economic/resources/detail.html", context)
