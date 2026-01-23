# economic/services/views/package_detail.py
from __future__ import annotations

from django.shortcuts import render, get_object_or_404

from ..models import ServicePackage


def package_detail_view(request, slug):
    package = get_object_or_404(
        ServicePackage.objects.filter(is_active=True).prefetch_related("services", "features"),
        slug=slug,
    )
    return render(
        request,
        "economic/services/package_detail.html",
        {
            "package": package,
        },
    )






# # economic/services/views/package_detail.py
# from __future__ import annotations

# from django.shortcuts import render, get_object_or_404

# from ..models import ServicePackage


# def package_detail_view(request, slug):
#     package = get_object_or_404(
#         ServicePackage.objects.filter(is_active=True).prefetch_related("services", "features"),
#         slug=slug,
#     )
#     return render(request, "economic/services/package_detail.html", {"package": package})
