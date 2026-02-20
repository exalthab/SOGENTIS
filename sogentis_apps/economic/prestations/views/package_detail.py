# economic/prestations/views/package_detail.py
from __future__ import annotations

from django.shortcuts import get_object_or_404, render


def _cur(request) -> str:
    return (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()


def _safe_prefetch_related(qs, *fields: str):
    try:
        existing = {f.name for f in qs.model._meta.get_fields()}
        valid = [f for f in fields if f in existing]
        return qs.prefetch_related(*valid) if valid else qs
    except Exception:
        return qs


def package_detail_view(request, slug: str):

    from ..models import PrestationPackage

    qs = PrestationPackage.objects.all()

    # -------------------------------------------------
    # Active filter (if exists)
    # -------------------------------------------------
    try:
        if "is_active" in {f.name for f in PrestationPackage._meta.get_fields()}:
            qs = qs.filter(is_active=True)
    except Exception:
        pass

    # -------------------------------------------------
    # Prefetch safely
    # -------------------------------------------------
    qs = _safe_prefetch_related(qs, "prestations", "features")

    # -------------------------------------------------
    # Parler support (safe)
    # -------------------------------------------------
    language = getattr(request, "LANGUAGE_CODE", None)
    if hasattr(qs, "translated") and language:
        try:
            qs = qs.translated(language)
        except Exception:
            pass
    elif hasattr(qs, "language"):
        try:
            qs = qs.language()
        except Exception:
            pass

    # -------------------------------------------------
    # Get object
    # -------------------------------------------------
    package = get_object_or_404(qs, slug=slug)

    # -------------------------------------------------
    # Normalize Display Fields (CRITICAL)
    # -------------------------------------------------

    package.display_title = (
        getattr(package, "title", None)
        or getattr(package, "slug", "")
    )

    package.display_excerpt = (
        getattr(package, "short_description", None)
        or getattr(package, "description", None)
        or ""
    )

    package.display_price = (
        getattr(package, "total_price", None)
        or getattr(package, "price", None)
        or getattr(package, "base_price", None)
    )

    package.display_currency = _cur(request)

    # -------------------------------------------------
    # Normalize related prestations (optional safety)
    # -------------------------------------------------

    if hasattr(package, "prestations"):
        for p in package.prestations.all():
            p.display_title = (
                getattr(p, "title", None)
                or getattr(p, "slug", "")
            )
            p.display_price = (
                getattr(p, "min_price", None)
                or getattr(p, "price", None)
                or getattr(p, "base_price", None)
            )

    # -------------------------------------------------
    # Render
    # -------------------------------------------------

    return render(
        request,
        "economic/prestations/package_detail.html",
        {
            "package": package,
            "cur": package.display_currency,
        },
    )






# # economic/prestations/views/package_detail.py
# from __future__ import annotations

# from django.shortcuts import get_object_or_404, render

# from ..models import PrestationPackage


# def package_detail_view(request, slug: str):
#     qs = PrestationPackage.objects.filter(is_active=True)
#     try:
#         qs = qs.prefetch_related("prestations", "features")
#     except Exception:
#         try:
#             qs = qs.prefetch_related("features")
#         except Exception:
#             pass

#     if hasattr(qs, "language"):
#         try:
#             qs = qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     package = get_object_or_404(qs, slug=slug)

#     return render(
#         request,
#         "economic/prestations/package_detail.html",
#         {
#             "package": package,
#             "cur": (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper(),
#         },
#     )







# # economic/prestations/views/package_detail.py - good
# from __future__ import annotations

# from django.shortcuts import get_object_or_404, render

# from ..models import PrestationPackage


# def package_detail_view(request, slug: str):
#     package = get_object_or_404(
#         PrestationPackage.objects.filter(is_active=True).prefetch_related("prestations", "features"),
#         slug=slug,
#     )
#     return render(
#         request,
#         "economic/prestations/package_detail.html",
#         {
#             "package": package,
#         },
#     )






# # economic/prestations/views/package_detail.py
# from __future__ import annotations

# from django.shortcuts import render, get_object_or_404

# from ..models import ServicePackage


# def package_detail_view(request, slug):
#     package = get_object_or_404(
#         ServicePackage.objects.filter(is_active=True).prefetch_related("services", "features"),
#         slug=slug,
#     )
#     return render(
#         request,
#         "economic/services/package_detail.html",
#         {
#             "package": package,
#         },
#     )






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
