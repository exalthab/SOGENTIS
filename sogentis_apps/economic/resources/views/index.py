# economic/resources/views/index.py
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from ..models import ResourceMod, ResourceCategory


def resources_mod_index_view(request):
    """
    Page d’index des ressources
    """
    cat_slug = (request.GET.get("cat") or "").strip()

    # ✅ Filtrer sur is_active pour ResourceCategory
    categories = (
        ResourceCategory.objects
        .filter(is_active=True)
        .order_by("created_at", "id")
    )

    # ✅ Filtrer sur is_published pour ResourceMod
    resources = (
        ResourceMod.objects
        .filter(is_published=True)
        .select_related("category")
        .order_by("-created_at", "-id")
    )

    current_category = None
    if cat_slug:
        current_category = categories.filter(slug=cat_slug).first()
        if current_category:
            resources = resources.filter(category=current_category)

    context = {
        "page_title": _("Ressources"),
        "categories": categories,
        "resources": resources,
        "current_category": current_category,
    }
    return render(request, "economic/resources/index.html", context)









# from django.shortcuts import render, get_object_or_404
# from ..models.resource_mod import ResourceMod


# def resources_mod_index_view(request):
#     resources = ResourceMod.objects.filter(is_active=True).order_by("-created_at")
#     return render(
#         request,
#         "economic/resources/index.html",
#         {"resources": resources},
#     )







# from django.shortcuts import render
# from ..models.resource_mod import ResourceMod


# def resources_mod_index_view(request):
#     return render(request, "economic/resources/index.html", {
#         "resources": ResourceMod.objects.all()
#     })
