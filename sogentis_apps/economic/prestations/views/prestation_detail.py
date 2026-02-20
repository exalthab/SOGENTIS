# economic/prestations/views/prestation_detail.py
from __future__ import annotations

from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from ..models import Prestation, PrestationPackage


def _model_field_names(model) -> set[str]:
    """Return the set of field names for a given Django model."""
    try:
        return {f.name for f in model._meta.get_fields()}
    except Exception:
        return set()


def prestation_detail_view(request, slug: str):
    """Render the detail page for a single prestation."""
    # Base queryset: only active prestations
    qs = Prestation.objects.filter(is_active=True)
    try:
        qs = qs.select_related("category").prefetch_related("features")
    except Exception:
        pass

    # Optional language support
    if hasattr(qs, "language"):
        try:
            qs = qs.language()  # type: ignore[attr-defined]
        except Exception:
            pass

    # Get the prestation or 404
    prestation = get_object_or_404(qs, slug=slug)

    # Currency from session or default
    cur = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()

    # Safe template fields
    title = getattr(prestation, "title", None) or getattr(prestation, "slug", "Prestation")
    excerpt = getattr(prestation, "short_description", None) or getattr(prestation, "summary", "")
    body = getattr(prestation, "description", None) or getattr(prestation, "content", None) or getattr(prestation, "long_description", "")
    price = getattr(prestation, "display_price", None) or getattr(prestation, "min_price", None) or getattr(prestation, "price", None)
    delivery = getattr(prestation, "delivery_days", None) or getattr(prestation, "delivery_time", None)
    duration = getattr(prestation, "duration_days", None) or getattr(prestation, "duration", None)

    # Safely get plans (ManyToMany or reverse relation)
    plans = getattr(prestation, "plans", None)
    if plans is None:
        plans = getattr(prestation, "prestationplan_set", None)
        if plans:
            plans = plans.all()
        else:
            plans = []
    else:
        if hasattr(plans, "all"):
            plans = plans.all()

    # Related packages
    pkg_fields = _model_field_names(PrestationPackage)
    packages = PrestationPackage.objects.filter(is_active=True)

    if "slug" in pkg_fields:
        packages = packages.exclude(slug__isnull=True).exclude(slug="")

    # Filter packages linked to this prestation
    rel_q = Q()
    if "prestations" in pkg_fields:
        rel_q |= Q(prestations=prestation)
    if "services" in pkg_fields:
        rel_q |= Q(services=prestation)

    packages = packages.filter(rel_q).distinct() if rel_q else packages.none()

    try:
        packages = packages.prefetch_related("features")
    except Exception:
        pass

    packages = packages.order_by("-is_featured", "order", "-created_at", "-id")

    # Optional language support for packages
    if hasattr(packages, "language"):
        try:
            packages = packages.language()  # type: ignore[attr-defined]
        except Exception:
            pass

    return render(
        request,
        "economic/prestations/prestations_detail.html",
        {
            "cur": cur,
            "prestation": prestation,
            "packages": packages,
            "title": title,
            "excerpt": excerpt,
            "body": body,
            "price": price,
            "delivery": delivery,
            "duration": duration,
            "plans": plans,
        },
    )







# # economic/prestations/views/prestation_detail.py
# from __future__ import annotations

# from django.db.models import Q
# from django.shortcuts import get_object_or_404, render

# from ..models import Prestation, PrestationPackage


# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def prestation_detail_view(request, slug: str):
#     qs = Prestation.objects.filter(is_active=True)
#     try:
#         qs = qs.select_related("category").prefetch_related("features")
#     except Exception:
#         pass

#     if hasattr(qs, "language"):
#         try:
#             qs = qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     prestation = get_object_or_404(qs, slug=slug)

#     cur = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()

#     pkg_fields = _model_field_names(PrestationPackage)
#     packages = PrestationPackage.objects.filter(is_active=True)

#     if "slug" in pkg_fields:
#         packages = packages.exclude(slug__isnull=True).exclude(slug="")

#     rel_q = Q()
#     if "prestations" in pkg_fields:
#         rel_q |= Q(prestations=prestation)
#     if "services" in pkg_fields:
#         rel_q |= Q(services=prestation)

#     packages = packages.filter(rel_q).distinct() if rel_q else packages.none()

#     try:
#         packages = packages.prefetch_related("features")
#     except Exception:
#         pass

#     packages = packages.order_by("-is_featured", "order", "-created_at", "-id")

#     if hasattr(packages, "language"):
#         try:
#             packages = packages.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     return render(
#         request,
#         "economic/prestations/prestations_detail.html",
#         {
#             "cur": cur,
#             "prestation": prestation,
#             "packages": packages,
#         },
#     )







# # economic/prestations/views/prestation_detail.py - good
# from __future__ import annotations

# from django.db.models import Q
# from django.shortcuts import get_object_or_404, render

# from ..models import Prestation, PrestationPackage


# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def prestation_detail_view(request, slug: str):
#     qs = Prestation.objects.filter(is_active=True).select_related("category").prefetch_related("features")
#     if hasattr(qs, "language"):
#         try:
#             qs = qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     prestation = get_object_or_404(qs, slug=slug)

#     cur = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").strip() or "XOF"

#     # packs qui contiennent cette prestation (compat prestations/services)
#     pkg_fields = _model_field_names(PrestationPackage)
#     packages = PrestationPackage.objects.filter(is_active=True)

#     if "slug" in pkg_fields:
#         packages = packages.exclude(slug__isnull=True).exclude(slug="")

#     rel_q = Q()
#     if "prestations" in pkg_fields:
#         rel_q |= Q(prestations=prestation)
#     if "services" in pkg_fields:
#         rel_q |= Q(services=prestation)

#     if rel_q:
#         packages = packages.filter(rel_q).distinct()
#     else:
#         packages = packages.none()

#     packages = packages.prefetch_related("features").order_by("-is_featured", "order", "-created_at", "-id")

#     if hasattr(packages, "language"):
#         try:
#             packages = packages.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     return render(
#         request,
#         "economic/prestations/prestations_detail.html",
#         {
#             "cur": cur,
#             "prestation": prestation,
#             "service": prestation,  # compat si tu as encore du legacy
#             "packages": packages,
#         },
#     )







# # economic/prestations/views/prestations_detail.py
# from __future__ import annotations

# from django.shortcuts import get_object_or_404, render

# from ..models import Prestation, PrestationPackage


# def prestation_detail_view(request, slug: str):
#     prestation = get_object_or_404(
#         Prestation.objects.filter(is_active=True)
#         .select_related("category")
#         .prefetch_related("features"),
#         slug=slug,
#     )

#     # packs qui contiennent cette prestation (utile UX)
#     packages = (
#         PrestationPackage.objects.filter(is_active=True, prestations=prestation)
#         .prefetch_related("features")
#         .order_by("-is_featured", "order", "-created_at", "-id")
#     )

#     return render(
#         request,
#         "economic/prestations/prestation_detail.html",
#         {
#             "prestation": prestation,
#             # compat si une partie du template utilise encore "service"
#             "service": prestation,
#             "packages": packages,
#         },
#     )






# # economic/prestations/views/prestations_detail.py
# from __future__ import annotations

# from django.shortcuts import render, get_object_or_404

# from ..models import Service, ServicePackage


# def service_detail_view(request, slug):
#     service = get_object_or_404(
#         Service.objects.filter(is_active=True).select_related("category").prefetch_related("features"),
#         slug=slug,
#     )

#     # packs qui contiennent ce service (utile UX)
#     packages = (
#         ServicePackage.objects.filter(is_active=True, services=service)
#         .prefetch_related("features")
#         .order_by("-is_featured", "order", "-created_at", "-id")
#     )

#     return render(
#         request,
#         "economic/services/service_detail.html",
#         {
#             "service": service,
#             "packages": packages,
#         },
#     )




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
