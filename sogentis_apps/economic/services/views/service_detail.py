# economic/services/views/service_detail.py
from __future__ import annotations

from django.shortcuts import render, get_object_or_404

from ..models import Service, ServicePackage


def service_detail_view(request, slug):
    service = get_object_or_404(
        Service.objects.filter(is_active=True).select_related("category").prefetch_related("features"),
        slug=slug,
    )

    # packs qui contiennent ce service (utile UX)
    packages = (
        ServicePackage.objects.filter(is_active=True, services=service)
        .prefetch_related("features")
        .order_by("-is_featured", "order", "-created_at", "-id")
    )

    return render(
        request,
        "economic/services/service_detail.html",
        {
            "service": service,
            "packages": packages,
        },
    )




# # economic/services/views/service_detail.py
# from django.shortcuts import render, get_object_or_404
# from ..models.service import Service

# def service_detail_view(request, slug):
#     service = get_object_or_404(
#         Service,
#         slug=slug,  # make sure Service has a 'slug' field
#         is_active=True
#     )
#     return render(request, "economic/services/service_detail.html", {"service": service})
