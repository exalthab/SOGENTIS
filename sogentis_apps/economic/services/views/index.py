# economic/services/views/index.py
from __future__ import annotations

from django.db.models import Q
from django.shortcuts import render

from ..models import Service, ServiceCategory, ServicePackage


def services_index_view(request):
    services = (
        Service.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("features")
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        services = services.filter(
            Q(translations__title__icontains=q)
            | Q(translations__short_description__icontains=q)
            | Q(slug__icontains=q)
        ).distinct()

    cat = (request.GET.get("cat") or "").strip()
    if cat:
        services = services.filter(category__slug=cat)

    typ = (request.GET.get("type") or "").strip()
    if typ:
        services = services.filter(service_type=typ)

    services = services.order_by("-is_featured", "order", "-created_at", "-id")

    categories = ServiceCategory.objects.filter(is_active=True).order_by("id")

    packages = (
        ServicePackage.objects.filter(is_active=True)
        .prefetch_related("services", "features")
        .order_by("-is_featured", "order", "-created_at", "-id")
    )

    # ✅ compat : si tu as Service.ServiceType (TextChoices), sinon fallback sur SERVICE_TYPE_CHOICES
    service_type_choices = []
    if hasattr(Service, "ServiceType"):
        service_type_choices = Service.ServiceType.choices
    else:
        service_type_choices = getattr(Service, "SERVICE_TYPE_CHOICES", [])

    return render(
        request,
        "economic/services/index.html",
        {
            "services": services,
            "categories": categories,
            "packages": packages,
            "service_type_choices": service_type_choices,
            "q": q,
            "cat": cat,
            "type": typ,
        },
    )





# # economic/services/views/index.py
# from django.shortcuts import render
# from django.db.models import Q

# from ..models import Service, ServiceCategory, ServicePackage


# def services_index_view(request):
#     qs = Service.objects.filter(is_active=True).select_related("category")

#     q = (request.GET.get("q") or "").strip()
#     if q:
#         qs = qs.filter(
#             Q(translations__title__icontains=q)
#             | Q(translations__short_description__icontains=q)
#             | Q(slug__icontains=q)
#         ).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         qs = qs.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         qs = qs.filter(service_type=typ)

#     qs = qs.order_by("-is_featured", "-created_at", "-id")

#     categories = ServiceCategory.objects.filter(is_active=True).order_by("-created_at", "-id")
#     packages = ServicePackage.objects.filter(is_active=True).prefetch_related("services").order_by("-created_at", "-id")

#     # choices (pour filtre)
#     service_type_choices = getattr(Service, "SERVICE_TYPE_CHOICES", [])

#     return render(
#         request,
#         "economic/services/index.html",
#         {
#             "services": qs,
#             "categories": categories,
#             "packages": packages,
#             "service_type_choices": service_type_choices,
#         },
#     )




# # economic/services/views/index.py
# from django.shortcuts import render
# from ..models.service import Service


# def services_index_view(request):
#     qs = (
#         Service.objects.filter(is_active=True)
#         .select_related("category")
#         .order_by("-is_featured", "-created_at", "-id")
#     )
#     return render(
#         request,
#         "economic/services/index.html",
#         {"services": qs},
#     )
