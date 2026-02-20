# economic/prestations/views/index.py
from __future__ import annotations

from typing import Iterable
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# =========================================================
# Utilities
# =========================================================

def _cur(request: HttpRequest) -> str:
    return (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()


def _model_field_names(model) -> set[str]:
    try:
        return {f.name for f in model._meta.get_fields() if getattr(f, "name", None)}
    except Exception:
        return set()


def _pick_existing(candidates: Iterable[str], existing: set[str]) -> str | None:
    for name in candidates:
        if name in existing:
            return name
    return None


def _safe_select_related(qs, *fields: str):
    existing = _model_field_names(qs.model)
    valid = [f for f in fields if f in existing]
    return qs.select_related(*valid) if valid else qs


def _safe_prefetch_related(qs, *fields: str):
    existing = _model_field_names(qs.model)
    valid = [f for f in fields if f in existing]
    return qs.prefetch_related(*valid) if valid else qs


# =========================================================
# Sorting
# =========================================================

def _safe_ordering(existing: set[str], sort: str) -> list[str]:
    base = []
    for f in ("-is_featured", "order", "-created_at", "-id"):
        if f.lstrip("-") in existing:
            base.append(f)

    if sort == "new":
        return [f for f in ("-created_at", "-id") if f.lstrip("-") in existing] or base

    if sort == "popular":
        for f in (
            "-views_count",
            "-orders_count",
            "-sales_count",
            "-popularity",
        ):
            if f.lstrip("-") in existing:
                return [f]
        return base

    if sort in ("price_asc", "price_desc"):
        price_field = _pick_existing(
            ("min_price", "price", "base_price", "amount"),
            existing,
        )
        if price_field:
            prefix = "" if sort == "price_asc" else "-"
            return [f"{prefix}{price_field}"]
        return base

    return base


# =========================================================
# Filters
# =========================================================

def _apply_search(qs, q: str, existing: set[str]):
    q = (q or "").strip()
    if not q:
        return qs

    tokens = [t for t in q.split() if t]
    if not tokens:
        return qs

    fields = [
        f for f in (
            "title",
            "slug",
            "short_description",
            "description",
        )
        if f in existing
    ]

    cond = Q()
    for token in tokens:
        token_q = Q()
        for f in fields:
            token_q |= Q(**{f"{f}__icontains": token})
        cond &= token_q

    return qs.filter(cond).distinct()


def _apply_type_filter(qs, typ: str, existing: set[str]):
    typ = (typ or "").strip()
    if not typ:
        return qs

    field_name = _pick_existing(
        ("prestation_type", "service_type", "type"),
        existing,
    )
    if not field_name:
        return qs

    return qs.filter(**{field_name: typ})


# =========================================================
# MAIN VIEW
# =========================================================

def prestations_index_view(request: HttpRequest) -> HttpResponse:
    from ..models import Prestation, PrestationCategory

    try:
        from ..models import PrestationPackage
    except Exception:
        PrestationPackage = None

    q = (request.GET.get("q") or "").strip()
    typ = (request.GET.get("type") or "").strip()
    cat = (request.GET.get("cat") or "").strip()
    sort = (request.GET.get("sort") or "").strip().lower()
    page = request.GET.get("page") or "1"
    packs_page = request.GET.get("packs_page") or "1"

    # =====================================================
    # PRESTATIONS
    # =====================================================

    existing = _model_field_names(Prestation)
    prestations_qs = Prestation.objects.all()

    if "is_active" in existing:
        prestations_qs = prestations_qs.filter(is_active=True)

    prestations_qs = _safe_select_related(prestations_qs, "category")
    prestations_qs = _safe_prefetch_related(prestations_qs, "features")

    prestations_qs = _apply_search(prestations_qs, q, existing)
    prestations_qs = _apply_type_filter(prestations_qs, typ, existing)

    if cat and "category" in existing:
        prestations_qs = prestations_qs.filter(category__slug=cat)

    ordering = _safe_ordering(existing, sort)
    prestations_qs = prestations_qs.order_by(*(ordering or ["-id"]))

    paginator = Paginator(prestations_qs, 12)

    try:
        prestations_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        prestations_page = paginator.page(1)

    for obj in prestations_page.object_list:
        obj.display_title = (
            getattr(obj, "title", None)
            or getattr(obj, "slug", "")
        )
        obj.display_excerpt = (
            getattr(obj, "short_description", None)
            or getattr(obj, "description", "")
        )
        obj.display_price = (
            getattr(obj, "min_price", None)
            or getattr(obj, "price", None)
            or getattr(obj, "base_price", None)
        )

    # =====================================================
    # CATEGORIES
    # =====================================================

    categories_qs = PrestationCategory.objects.filter(is_active=True)

    # =====================================================
    # PACKAGES
    # =====================================================

    packages_page = None

    if PrestationPackage:
        p_existing = _model_field_names(PrestationPackage)
        packages_qs = PrestationPackage.objects.all()

        if "is_active" in p_existing:
            packages_qs = packages_qs.filter(is_active=True)

        packages_qs = _safe_prefetch_related(packages_qs, "prestations", "features")
        packages_qs = packages_qs.exclude(slug__isnull=True).exclude(slug="")

        packs_paginator = Paginator(packages_qs.order_by("-id"), 6)

        try:
            packages_page = packs_paginator.page(packs_page)
        except (PageNotAnInteger, EmptyPage):
            packages_page = packs_paginator.page(1)

        for obj in packages_page.object_list:
            obj.display_title = (
                getattr(obj, "title", None)
                or getattr(obj, "slug", "")
            )
            obj.display_excerpt = (
                getattr(obj, "short_description", None)
                or getattr(obj, "description", "")
            )
            obj.display_price = (
                getattr(obj, "total_price", None)
                or getattr(obj, "price", None)
                or getattr(obj, "base_price", None)
            )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "cur": _cur(request),

        "prestations": prestations_page.object_list,
        "page_obj": prestations_page,
        "paginator": paginator,
        "is_paginated": paginator.num_pages > 1,

        "packages": packages_page.object_list if packages_page else [],
        "packs_page_obj": packages_page,

        "categories": categories_qs,

        "q": q,
        "typ": typ,
        "cat": cat,
        "sort": sort,
    }

    return render(request, "economic/prestations/index.html", context)







# # economic/prestations/views/index.py
# from __future__ import annotations

# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.db.models import Q
# from django.shortcuts import render

# from ..models import Prestation, PrestationCategory, PrestationPackage


# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def _safe_select_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.select_related(*keep) if keep else qs


# def _safe_prefetch_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.prefetch_related(*keep) if keep else qs


# def _safe_order_by(qs, candidates: list[str]):
#     available = _model_field_names(qs.model)
#     keep: list[str] = []
#     for name in candidates:
#         field = name.lstrip("-")
#         if field in available:
#             keep.append(name)
#     return qs.order_by(*keep) if keep else qs.order_by("-id")


# def _is_parler_model(model) -> bool:
#     return bool(getattr(model, "_parler_meta", None)) or "translations" in _model_field_names(model)


# def _get_prestation_type_choices() -> list[tuple[str, str]]:
#     # ✅ uniquement prestations (aucun "service")
#     if hasattr(Prestation, "PrestationType"):
#         return list(Prestation.PrestationType.choices)  # type: ignore[attr-defined]
#     return list(getattr(Prestation, "PRESTATION_TYPE_CHOICES", []) or [])


# def prestations_index_view(request):
#     # devise (évite request.session partout dans les templates)
#     cur = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()

#     # -----------------------------
#     # Prestations queryset
#     # -----------------------------
#     prestations_qs = Prestation.objects.filter(is_active=True)
#     prestations_qs = _safe_select_related(prestations_qs, "category")
#     prestations_qs = _safe_prefetch_related(prestations_qs, "features")

#     if hasattr(prestations_qs, "language"):
#         try:
#             prestations_qs = prestations_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Filters
#     # -----------------------------
#     q = (request.GET.get("q") or "").strip()
#     if q:
#         if _is_parler_model(Prestation):
#             prestations_qs = prestations_qs.filter(
#                 Q(translations__title__icontains=q)
#                 | Q(translations__short_description__icontains=q)
#                 | Q(slug__icontains=q)
#             ).distinct()
#         else:
#             f = _model_field_names(Prestation)
#             cond = Q(slug__icontains=q)
#             if "title" in f:
#                 cond |= Q(title__icontains=q)
#             if "short_description" in f:
#                 cond |= Q(short_description__icontains=q)
#             if "description" in f:
#                 cond |= Q(description__icontains=q)
#             prestations_qs = prestations_qs.filter(cond).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         prestations_qs = prestations_qs.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         # ✅ plus de "service_type"
#         prestations_qs = prestations_qs.filter(prestation_type=typ)

#     prestations_qs = _safe_order_by(prestations_qs, ["-is_featured", "order", "-created_at", "-id"])

#     # -----------------------------
#     # Categories queryset
#     # -----------------------------
#     categories_qs = PrestationCategory.objects.filter(is_active=True)
#     categories_qs = _safe_order_by(categories_qs, ["order", "id"])

#     if hasattr(categories_qs, "language"):
#         try:
#             categories_qs = categories_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Packages queryset
#     # -----------------------------
#     packages_qs = PrestationPackage.objects.filter(is_active=True)
#     # ✅ pas de "services" ici
#     packages_qs = _safe_prefetch_related(packages_qs, "prestations", "features")
#     packages_qs = _safe_order_by(packages_qs, ["-is_featured", "order", "-created_at", "-id"])
#     # ✅ évite /packs/None/
#     packages_qs = packages_qs.exclude(slug__isnull=True).exclude(slug="")

#     if hasattr(packages_qs, "language"):
#         try:
#             packages_qs = packages_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Pagination
#     # -----------------------------
#     per_page = request.GET.get("per_page") or "12"
#     try:
#         per_page_int = max(1, min(int(per_page), 60))
#     except Exception:
#         per_page_int = 12

#     page = request.GET.get("page") or "1"
#     paginator = Paginator(prestations_qs, per_page_int)
#     try:
#         prestations_page = paginator.page(page)
#     except PageNotAnInteger:
#         prestations_page = paginator.page(1)
#     except EmptyPage:
#         prestations_page = paginator.page(paginator.num_pages)

#     packs_page = request.GET.get("packs_page") or "1"
#     packs_per_page = request.GET.get("packs_per_page") or "6"
#     try:
#         packs_per_page_int = max(1, min(int(packs_per_page), 24))
#     except Exception:
#         packs_per_page_int = 6

#     packs_paginator = Paginator(packages_qs, packs_per_page_int)
#     try:
#         packages_page = packs_paginator.page(packs_page)
#     except PageNotAnInteger:
#         packages_page = packs_paginator.page(1)
#     except EmptyPage:
#         packages_page = packs_paginator.page(packs_paginator.num_pages)

#     # -----------------------------
#     # Normalisation d'affichage (supprime .name partout)
#     # -----------------------------
#     for obj in prestations_page.object_list:
#         obj.display_title = getattr(obj, "title", "") or getattr(obj, "slug", "")
#         obj.display_price = getattr(obj, "base_price", None)

#     for obj in categories_qs:
#         obj.display_title = getattr(obj, "title", "") or getattr(obj, "slug", "")

#     for obj in packages_page.object_list:
#         obj.display_title = getattr(obj, "title", "") or getattr(obj, "slug", "")
#         obj.display_price = (
#             getattr(obj, "total_price", None)
#             or getattr(obj, "price", None)
#             or getattr(obj, "base_price", None)
#         )

#     return render(
#         request,
#         "economic/prestations/index.html",
#         {
#             "cur": cur,

#             "prestations": prestations_page.object_list,
#             "page_obj": prestations_page,
#             "paginator": paginator,
#             "is_paginated": paginator.num_pages > 1,
#             "per_page": per_page_int,

#             "packages": packages_page.object_list,
#             "packs_page_obj": packages_page,
#             "packs_paginator": packs_paginator,
#             "packs_is_paginated": packs_paginator.num_pages > 1,
#             "packs_per_page": packs_per_page_int,

#             "categories": categories_qs,
#             "prestation_type_choices": _get_prestation_type_choices(),

#             "q": q,
#             "cat": cat,
#             "type": typ,
#         },
#     )




# # economic/prestations/views/index.py -good
# from __future__ import annotations

# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.db.models import Q
# from django.shortcuts import render

# from ..models import Prestation, PrestationCategory, PrestationPackage


# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def _safe_select_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.select_related(*keep) if keep else qs


# def _safe_prefetch_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.prefetch_related(*keep) if keep else qs


# def _safe_order_by(qs, candidates: list[str]):
#     available = _model_field_names(qs.model)
#     keep: list[str] = []
#     for name in candidates:
#         field = name.lstrip("-")
#         if field in available:
#             keep.append(name)
#     return qs.order_by(*keep) if keep else qs.order_by("-id")


# def _is_parler_model(model) -> bool:
#     return bool(getattr(model, "_parler_meta", None)) or "translations" in _model_field_names(model)


# def _get_prestation_type_choices() -> list[tuple[str, str]]:
#     # ✅ uniquement prestations (aucun "service")
#     if hasattr(Prestation, "PrestationType"):
#         return list(Prestation.PrestationType.choices)  # type: ignore[attr-defined]
#     return list(getattr(Prestation, "PRESTATION_TYPE_CHOICES", []) or [])


# def prestations_index_view(request):
#     # devise (évite request.session partout dans les templates)
#     cur = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()

#     # -----------------------------
#     # Prestations queryset
#     # -----------------------------
#     prestations_qs = Prestation.objects.filter(is_active=True)
#     prestations_qs = _safe_select_related(prestations_qs, "category")
#     prestations_qs = _safe_prefetch_related(prestations_qs, "features")

#     if hasattr(prestations_qs, "language"):
#         try:
#             prestations_qs = prestations_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Filters
#     # -----------------------------
#     q = (request.GET.get("q") or "").strip()
#     if q:
#         if _is_parler_model(Prestation):
#             prestations_qs = prestations_qs.filter(
#                 Q(translations__title__icontains=q)
#                 | Q(translations__short_description__icontains=q)
#                 | Q(slug__icontains=q)
#             ).distinct()
#         else:
#             f = _model_field_names(Prestation)
#             cond = Q(slug__icontains=q)
#             if "title" in f:
#                 cond |= Q(title__icontains=q)
#             if "short_description" in f:
#                 cond |= Q(short_description__icontains=q)
#             if "description" in f:
#                 cond |= Q(description__icontains=q)
#             prestations_qs = prestations_qs.filter(cond).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         prestations_qs = prestations_qs.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         # ✅ plus de "service_type"
#         prestations_qs = prestations_qs.filter(prestation_type=typ)

#     prestations_qs = _safe_order_by(prestations_qs, ["-is_featured", "order", "-created_at", "-id"])

#     # -----------------------------
#     # Categories queryset
#     # -----------------------------
#     categories_qs = PrestationCategory.objects.filter(is_active=True)
#     categories_qs = _safe_order_by(categories_qs, ["order", "id"])

#     if hasattr(categories_qs, "language"):
#         try:
#             categories_qs = categories_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Packages queryset
#     # -----------------------------
#     packages_qs = PrestationPackage.objects.filter(is_active=True)
#     # ✅ pas de "services" ici
#     packages_qs = _safe_prefetch_related(packages_qs, "prestations", "features")
#     packages_qs = _safe_order_by(packages_qs, ["-is_featured", "order", "-created_at", "-id"])
#     # ✅ évite /packs/None/
#     packages_qs = packages_qs.exclude(slug__isnull=True).exclude(slug="")

#     if hasattr(packages_qs, "language"):
#         try:
#             packages_qs = packages_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Pagination
#     # -----------------------------
#     per_page = request.GET.get("per_page") or "12"
#     try:
#         per_page_int = max(1, min(int(per_page), 60))
#     except Exception:
#         per_page_int = 12

#     page = request.GET.get("page") or "1"
#     paginator = Paginator(prestations_qs, per_page_int)
#     try:
#         prestations_page = paginator.page(page)
#     except PageNotAnInteger:
#         prestations_page = paginator.page(1)
#     except EmptyPage:
#         prestations_page = paginator.page(paginator.num_pages)

#     packs_page = request.GET.get("packs_page") or "1"
#     packs_per_page = request.GET.get("packs_per_page") or "6"
#     try:
#         packs_per_page_int = max(1, min(int(packs_per_page), 24))
#     except Exception:
#         packs_per_page_int = 6

#     packs_paginator = Paginator(packages_qs, packs_per_page_int)
#     try:
#         packages_page = packs_paginator.page(packs_page)
#     except PageNotAnInteger:
#         packages_page = packs_paginator.page(1)
#     except EmptyPage:
#         packages_page = packs_paginator.page(packs_paginator.num_pages)

#     # -----------------------------
#     # Normalisation d'affichage (supprime .name partout)
#     # -----------------------------
#     for obj in prestations_page.object_list:
#         obj.display_title = getattr(obj, "title", "") or getattr(obj, "slug", "")
#         obj.display_price = getattr(obj, "base_price", None)

#     for obj in categories_qs:
#         obj.display_title = getattr(obj, "title", "") or getattr(obj, "slug", "")

#     for obj in packages_page.object_list:
#         obj.display_title = getattr(obj, "title", "") or getattr(obj, "slug", "")
#         obj.display_price = (
#             getattr(obj, "total_price", None)
#             or getattr(obj, "price", None)
#             or getattr(obj, "base_price", None)
#         )

#     return render(
#         request,
#         "economic/prestations/index.html",
#         {
#             "cur": cur,

#             "prestations": prestations_page.object_list,
#             "page_obj": prestations_page,
#             "paginator": paginator,
#             "is_paginated": paginator.num_pages > 1,
#             "per_page": per_page_int,

#             "packages": packages_page.object_list,
#             "packs_page_obj": packages_page,
#             "packs_paginator": packs_paginator,
#             "packs_is_paginated": packs_paginator.num_pages > 1,
#             "packs_per_page": packs_per_page_int,

#             "categories": categories_qs,
#             "prestation_type_choices": _get_prestation_type_choices(),

#             "q": q,
#             "cat": cat,
#             "type": typ,
#         },
#     )







# # economic/prestations/views/index.py
# from __future__ import annotations

# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.db.models import Q
# from django.shortcuts import render

# from ..models import Prestation, PrestationCategory, PrestationPackage


# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def _safe_select_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.select_related(*keep) if keep else qs


# def _safe_prefetch_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.prefetch_related(*keep) if keep else qs


# def _safe_order_by(qs, candidates: list[str]):
#     available = _model_field_names(qs.model)
#     keep: list[str] = []
#     for name in candidates:
#         field = name.lstrip("-")
#         if field in available:
#             keep.append(name)
#     return qs.order_by(*keep) if keep else qs.order_by("-id")


# def _is_parler_model(model) -> bool:
#     return bool(getattr(model, "_parler_meta", None)) or "translations" in _model_field_names(model)


# def _get_prestation_type_choices() -> list[tuple[str, str]]:
#     # ✅ garde la compat si tu as gardé "ServiceType" sur Prestation
#     if hasattr(Prestation, "ServiceType"):
#         return list(Prestation.ServiceType.choices)  # type: ignore[attr-defined]
#     if hasattr(Prestation, "PrestationType"):
#         return list(Prestation.PrestationType.choices)  # type: ignore[attr-defined]
#     return list(getattr(Prestation, "SERVICE_TYPE_CHOICES", []) or getattr(Prestation, "PRESTATION_TYPE_CHOICES", []) or [])


# def prestations_index_view(request):
#     # -----------------------------
#     # Base queryset (prestations)
#     # -----------------------------
#     prestations_qs = Prestation.objects.filter(is_active=True)
#     prestations_qs = _safe_select_related(prestations_qs, "category")
#     prestations_qs = _safe_prefetch_related(prestations_qs, "features")

#     if hasattr(prestations_qs, "language"):
#         try:
#             prestations_qs = prestations_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Filters
#     # -----------------------------
#     q = (request.GET.get("q") or "").strip()
#     if q:
#         parler = _is_parler_model(Prestation)
#         if parler:
#             # ✅ parle: translations__title / short_description (mêmes champs que ton ancien modèle)
#             prestations_qs = prestations_qs.filter(
#                 Q(translations__title__icontains=q)
#                 | Q(translations__short_description__icontains=q)
#                 | Q(slug__icontains=q)
#             ).distinct()
#         else:
#             f = _model_field_names(Prestation)
#             cond = Q()
#             if "title" in f:
#                 cond |= Q(title__icontains=q)
#             if "short_description" in f:
#                 cond |= Q(short_description__icontains=q)
#             if "description" in f:
#                 cond |= Q(description__icontains=q)
#             cond |= Q(slug__icontains=q)
#             prestations_qs = prestations_qs.filter(cond).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         prestations_qs = prestations_qs.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         # ✅ compat: si ton champ s'appelle encore service_type
#         field_names = _model_field_names(Prestation)
#         if "service_type" in field_names:
#             prestations_qs = prestations_qs.filter(service_type=typ)
#         elif "prestation_type" in field_names:
#             prestations_qs = prestations_qs.filter(prestation_type=typ)

#     prestations_qs = _safe_order_by(prestations_qs, ["-is_featured", "order", "-created_at", "-id"])

#     # -----------------------------
#     # Categories (prestations)
#     # -----------------------------
#     categories_qs = PrestationCategory.objects.filter(is_active=True)
#     categories_qs = _safe_order_by(categories_qs, ["order", "id"])
#     if hasattr(categories_qs, "language"):
#         try:
#             categories_qs = categories_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Packages (prestations)
#     # -----------------------------
#     packages_qs = PrestationPackage.objects.filter(is_active=True)
#     # ✅ compat: ton M2M peut s'appeler "prestations" OU "services" selon refacto
#     packages_qs = _safe_prefetch_related(packages_qs, "prestations", "services", "features")
#     packages_qs = _safe_order_by(packages_qs, ["-is_featured", "order", "-created_at", "-id"])
#     if hasattr(packages_qs, "language"):
#         try:
#             packages_qs = packages_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Pagination
#     # -----------------------------
#     per_page = request.GET.get("per_page") or "12"
#     try:
#         per_page_int = max(1, min(int(per_page), 60))
#     except Exception:
#         per_page_int = 12

#     page = request.GET.get("page") or "1"
#     paginator = Paginator(prestations_qs, per_page_int)
#     try:
#         prestations_page = paginator.page(page)
#     except PageNotAnInteger:
#         prestations_page = paginator.page(1)
#     except EmptyPage:
#         prestations_page = paginator.page(paginator.num_pages)

#     packs_page = request.GET.get("packs_page") or "1"
#     packs_per_page = request.GET.get("packs_per_page") or "6"
#     try:
#         packs_per_page_int = max(1, min(int(packs_per_page), 24))
#     except Exception:
#         packs_per_page_int = 6

#     packs_paginator = Paginator(packages_qs, packs_per_page_int)
#     try:
#         packages_page = packs_paginator.page(packs_page)
#     except PageNotAnInteger:
#         packages_page = packs_paginator.page(1)
#     except EmptyPage:
#         packages_page = packs_paginator.page(packs_paginator.num_pages)

#     # -----------------------------
#     # Context
#     # -----------------------------
#     prestation_type_choices = _get_prestation_type_choices()

#     return render(
#         request,
#         "economic/prestations/index.html",
#         {
#             # ✅ contexte “prestations”
#             "prestations": prestations_page.object_list,
#             "page_obj": prestations_page,
#             "paginator": paginator,
#             "is_paginated": paginator.num_pages > 1,
#             "per_page": per_page_int,

#             "packages": packages_page.object_list,
#             "packs_page_obj": packages_page,
#             "packs_paginator": packs_paginator,
#             "packs_is_paginated": packs_paginator.num_pages > 1,
#             "packs_per_page": packs_per_page_int,

#             "categories": categories_qs,
#             "prestation_type_choices": prestation_type_choices,

#             "q": q,
#             "cat": cat,
#             "type": typ,
#         },
#     )






# # economic/prestations/views/index.py
# from __future__ import annotations

# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.db.models import Q
# from django.shortcuts import render

# from ..models import Service, ServiceCategory, ServicePackage


# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def _safe_select_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.select_related(*keep) if keep else qs


# def _safe_prefetch_related(qs, *fields: str):
#     available = _model_field_names(qs.model)
#     keep = [f for f in fields if f in available]
#     return qs.prefetch_related(*keep) if keep else qs


# def _safe_order_by(qs, candidates: list[str]):
#     available = _model_field_names(qs.model)
#     keep: list[str] = []
#     for name in candidates:
#         field = name.lstrip("-")
#         if field in available:
#             keep.append(name)
#     return qs.order_by(*keep) if keep else qs.order_by("-id")


# def _is_parler_model(model) -> bool:
#     # Parler expose souvent _parler_meta et une relation translations
#     return bool(getattr(model, "_parler_meta", None)) or "translations" in _model_field_names(model)


# def _get_service_type_choices() -> list[tuple[str, str]]:
#     if hasattr(Service, "ServiceType"):
#         return list(Service.ServiceType.choices)  # type: ignore[attr-defined]
#     return list(getattr(Service, "SERVICE_TYPE_CHOICES", []) or [])


# def services_index_view(request):
#     # -----------------------------
#     # Base queryset (services)
#     # -----------------------------
#     services_qs = Service.objects.filter(is_active=True)
#     services_qs = _safe_select_related(services_qs, "category")
#     services_qs = _safe_prefetch_related(services_qs, "features")

#     # parler : si applicable, force langue courante
#     if hasattr(services_qs, "language"):
#         try:
#             services_qs = services_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Filters
#     # -----------------------------
#     q = (request.GET.get("q") or "").strip()
#     if q:
#         parler = _is_parler_model(Service)
#         if parler:
#             services_qs = services_qs.filter(
#                 Q(translations__title__icontains=q)
#                 | Q(translations__short_description__icontains=q)
#                 | Q(slug__icontains=q)
#             ).distinct()
#         else:
#             # Fallback non-parler (adapte aux champs possibles)
#             # On essaie title/short_description/description si présents
#             f = _model_field_names(Service)
#             cond = Q()
#             if "title" in f:
#                 cond |= Q(title__icontains=q)
#             if "short_description" in f:
#                 cond |= Q(short_description__icontains=q)
#             if "description" in f:
#                 cond |= Q(description__icontains=q)
#             cond |= Q(slug__icontains=q)
#             services_qs = services_qs.filter(cond).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         services_qs = services_qs.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         services_qs = services_qs.filter(service_type=typ)

#     services_qs = _safe_order_by(services_qs, ["-is_featured", "order", "-created_at", "-id"])

#     # -----------------------------
#     # Categories
#     # -----------------------------
#     categories_qs = ServiceCategory.objects.filter(is_active=True)
#     categories_qs = _safe_order_by(categories_qs, ["order", "id"])
#     if hasattr(categories_qs, "language"):
#         try:
#             categories_qs = categories_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Packages
#     # -----------------------------
#     packages_qs = ServicePackage.objects.filter(is_active=True)
#     packages_qs = _safe_prefetch_related(packages_qs, "services", "features")
#     packages_qs = _safe_order_by(packages_qs, ["-is_featured", "order", "-created_at", "-id"])
#     if hasattr(packages_qs, "language"):
#         try:
#             packages_qs = packages_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Pagination
#     # -----------------------------
#     per_page = request.GET.get("per_page") or "12"
#     try:
#         per_page_int = max(1, min(int(per_page), 60))
#     except Exception:
#         per_page_int = 12

#     page = request.GET.get("page") or "1"
#     paginator = Paginator(services_qs, per_page_int)
#     try:
#         services_page = paginator.page(page)
#     except PageNotAnInteger:
#         services_page = paginator.page(1)
#     except EmptyPage:
#         services_page = paginator.page(paginator.num_pages)

#     packs_page = request.GET.get("packs_page") or "1"
#     packs_per_page = request.GET.get("packs_per_page") or "6"
#     try:
#         packs_per_page_int = max(1, min(int(packs_per_page), 24))
#     except Exception:
#         packs_per_page_int = 6

#     packs_paginator = Paginator(packages_qs, packs_per_page_int)
#     try:
#         packages_page = packs_paginator.page(packs_page)
#     except PageNotAnInteger:
#         packages_page = packs_paginator.page(1)
#     except EmptyPage:
#         packages_page = packs_paginator.page(packs_paginator.num_pages)

#     # -----------------------------
#     # Context
#     # -----------------------------
#     service_type_choices = _get_service_type_choices()

#     return render(
#         request,
#         "economic/services/index.html",
#         {
#             "services": services_page.object_list,  # compat template
#             "page_obj": services_page,
#             "paginator": paginator,
#             "is_paginated": paginator.num_pages > 1,
#             "per_page": per_page_int,

#             "packages": packages_page.object_list,  # compat template
#             "packs_page_obj": packages_page,
#             "packs_paginator": packs_paginator,
#             "packs_is_paginated": packs_paginator.num_pages > 1,
#             "packs_per_page": packs_per_page_int,

#             "categories": categories_qs,
#             "service_type_choices": service_type_choices,

#             "q": q,
#             "cat": cat,
#             "type": typ,  # ok si ton template l’utilise déjà
#             # Optionnel (plus clair):
#             # "service_type_selected": typ,
#         },
#     )





# # economic/services/views/index.py
# from __future__ import annotations

# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.db.models import Q
# from django.shortcuts import render

# from ..models import Service, ServiceCategory, ServicePackage


# def _get_service_type_choices() -> list[tuple[str, str]]:
#     # ✅ compat : si tu as Service.ServiceType (TextChoices), sinon fallback
#     if hasattr(Service, "ServiceType"):
#         return list(Service.ServiceType.choices)  # type: ignore[attr-defined]
#     return list(getattr(Service, "SERVICE_TYPE_CHOICES", []) or [])


# def services_index_view(request):
#     # -----------------------------
#     # Base queryset (services)
#     # -----------------------------
#     services_qs = (
#         Service.objects.filter(is_active=True)
#         .select_related("category")
#         .prefetch_related("features")
#     )

#     # django-parler : si dispo, on force la langue courante (sinon ignore)
#     # (parler QuerySet supporte .language())
#     if hasattr(services_qs, "language"):
#         try:
#             services_qs = services_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Filters
#     # -----------------------------
#     q = (request.GET.get("q") or "").strip()
#     if q:
#         services_qs = services_qs.filter(
#             Q(translations__title__icontains=q)
#             | Q(translations__short_description__icontains=q)
#             | Q(slug__icontains=q)
#         ).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         services_qs = services_qs.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         services_qs = services_qs.filter(service_type=typ)

#     services_qs = services_qs.order_by("-is_featured", "order", "-created_at", "-id")

#     # -----------------------------
#     # Categories
#     # -----------------------------
#     categories_qs = ServiceCategory.objects.filter(is_active=True).order_by("order", "id")
#     # parler (si applicable)
#     if hasattr(categories_qs, "language"):
#         try:
#             categories_qs = categories_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Packages
#     # -----------------------------
#     packages_qs = (
#         ServicePackage.objects.filter(is_active=True)
#         .prefetch_related("services", "features")
#         .order_by("-is_featured", "order", "-created_at", "-id")
#     )
#     if hasattr(packages_qs, "language"):
#         try:
#             packages_qs = packages_qs.language()  # type: ignore[attr-defined]
#         except Exception:
#             pass

#     # -----------------------------
#     # Pagination
#     # -----------------------------
#     # Services pagination
#     per_page = request.GET.get("per_page") or "12"
#     try:
#         per_page_int = max(1, min(int(per_page), 60))
#     except Exception:
#         per_page_int = 12

#     page = request.GET.get("page") or "1"
#     paginator = Paginator(services_qs, per_page_int)

#     try:
#         services_page = paginator.page(page)
#     except PageNotAnInteger:
#         services_page = paginator.page(1)
#     except EmptyPage:
#         services_page = paginator.page(paginator.num_pages)

#     # Packs pagination (optionnel)
#     packs_page = request.GET.get("packs_page") or "1"
#     packs_per_page = request.GET.get("packs_per_page") or "6"
#     try:
#         packs_per_page_int = max(1, min(int(packs_per_page), 24))
#     except Exception:
#         packs_per_page_int = 6

#     packs_paginator = Paginator(packages_qs, packs_per_page_int)
#     try:
#         packages_page = packs_paginator.page(packs_page)
#     except PageNotAnInteger:
#         packages_page = packs_paginator.page(1)
#     except EmptyPage:
#         packages_page = packs_paginator.page(packs_paginator.num_pages)

#     # -----------------------------
#     # Context
#     # -----------------------------
#     service_type_choices = _get_service_type_choices()

#     return render(
#         request,
#         "economic/services/index.html",
#         {
#             # services (paginés)
#             "services": services_page.object_list,  # compat avec ton template actuel
#             "page_obj": services_page,
#             "paginator": paginator,
#             "is_paginated": paginator.num_pages > 1,
#             "per_page": per_page_int,
#             # packs (paginés)
#             "packages": packages_page.object_list,  # compat avec ton template actuel
#             "packs_page_obj": packages_page,
#             "packs_paginator": packs_paginator,
#             "packs_is_paginated": packs_paginator.num_pages > 1,
#             "packs_per_page": packs_per_page_int,
#             # filtres + options
#             "categories": categories_qs,
#             "service_type_choices": service_type_choices,
#             "q": q,
#             "cat": cat,
#             "type": typ,
#         },
#     )







# # economic/services/views/index.py
# from __future__ import annotations

# from django.db.models import Q
# from django.shortcuts import render

# from ..models import Service, ServiceCategory, ServicePackage


# def services_index_view(request):
#     services = (
#         Service.objects.filter(is_active=True)
#         .select_related("category")
#         .prefetch_related("features")
#     )

#     q = (request.GET.get("q") or "").strip()
#     if q:
#         services = services.filter(
#             Q(translations__title__icontains=q)
#             | Q(translations__short_description__icontains=q)
#             | Q(slug__icontains=q)
#         ).distinct()

#     cat = (request.GET.get("cat") or "").strip()
#     if cat:
#         services = services.filter(category__slug=cat)

#     typ = (request.GET.get("type") or "").strip()
#     if typ:
#         services = services.filter(service_type=typ)

#     services = services.order_by("-is_featured", "order", "-created_at", "-id")

#     categories = ServiceCategory.objects.filter(is_active=True).order_by("id")

#     packages = (
#         ServicePackage.objects.filter(is_active=True)
#         .prefetch_related("services", "features")
#         .order_by("-is_featured", "order", "-created_at", "-id")
#     )

#     # ✅ compat : si tu as Service.ServiceType (TextChoices), sinon fallback sur SERVICE_TYPE_CHOICES
#     service_type_choices = []
#     if hasattr(Service, "ServiceType"):
#         service_type_choices = Service.ServiceType.choices
#     else:
#         service_type_choices = getattr(Service, "SERVICE_TYPE_CHOICES", [])

#     return render(
#         request,
#         "economic/services/index.html",
#         {
#             "services": services,
#             "categories": categories,
#             "packages": packages,
#             "service_type_choices": service_type_choices,
#             "q": q,
#             "cat": cat,
#             "type": typ,
#         },
#     )





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
