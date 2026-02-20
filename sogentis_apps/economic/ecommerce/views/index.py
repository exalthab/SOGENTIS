# economic/ecommerce/views/index.py
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Avg, Count, Max, Q
from django.shortcuts import render

from ..models.product import Product
from ..models.category import Category


def _has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def _safe_decimal(value, default=None):
    if value in (None, ""):
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def _get_category_by_slug(language: str, slug_value: str):
    """
    Supporte 2 cas :
    - slug est un champ traduit Parler (CategoryTranslation.slug)
    - slug est un champ normal (Category.slug)
    """
    slug_value = (slug_value or "").strip()
    if not slug_value:
        return None

    # 1) ✅ Cas Parler (slug traduit)
    try:
        return Category.objects.translated(language, slug=slug_value).get(is_active=True)
    except Exception:
        pass

    # 2) ✅ Fallback explicite sur translations
    try:
        return Category.objects.filter(
            is_active=True,
            translations__language_code=language,
            translations__slug=slug_value,
        ).get()
    except Exception:
        pass

    # 3) ✅ Dernier fallback : n'importe quelle langue
    try:
        return (
            Category.objects.filter(is_active=True, translations__slug=slug_value)
            .distinct()
            .first()
        )
    except Exception:
        return None


def _catalog_view(request, template_name: str, category_slug=None):
    language = request.LANGUAGE_CODE or "fr"

    # Base QS (perf + images + pricing)
    products_qs = (
        Product.objects.filter(is_active=True)
        .translated(language)
        .select_related("category", "vendor", "pricing")
        .prefetch_related("images")
    )
    categories_qs = Category.objects.filter(is_active=True).translated(language)

    q = (request.GET.get("q") or "").strip()
    sort = (request.GET.get("sort") or "").strip()
    badge = (request.GET.get("badge") or "").strip()
    category = (request.GET.get("category") or "").strip()
    price_max = _safe_decimal(request.GET.get("price_max"))
    rating = (request.GET.get("rating") or "").strip()
    page_number = request.GET.get("page") or 1

    current_category = None

    # ✅ Category filter: URL takes priority
    if category_slug:
        current_category = _get_category_by_slug(language, category_slug)
        if current_category:
            products_qs = products_qs.filter(category=current_category)
            category = category_slug
    elif category:
        current_category = _get_category_by_slug(language, category)
        if current_category:
            products_qs = products_qs.filter(category=current_category)

    # Search
    if q:
        products_qs = products_qs.filter(translations__name__icontains=q).distinct()

    # Max price for slider / UI (sur price actuel)
    max_price = products_qs.aggregate(max_price=Max("price"))["max_price"] or Decimal("0")

    if price_max is not None:
        products_qs = products_qs.filter(price__lte=price_max)

    # Badge filters
    if badge == "fast" and _has_field(Product, "fast_delivery"):
        products_qs = products_qs.filter(fast_delivery=True)

    if badge == "choice" and _has_field(Product, "is_featured"):
        products_qs = products_qs.filter(is_featured=True)

    # Sorting
    if sort == "new":
        products_qs = products_qs.order_by("-created_at")
    elif sort == "best":
        products_qs = products_qs.order_by("-created_at")
    elif sort == "price_asc":
        products_qs = products_qs.order_by("price")
    elif sort == "price_desc":
        products_qs = products_qs.order_by("-price")
    elif sort == "deals" and _has_field(Product, "is_featured"):
        products_qs = products_qs.filter(is_featured=True).order_by("-created_at")

    # ✅ Stats réelles: rating + reviews (Review.is_active & is_approved)
    products_qs = products_qs.annotate(
        reviews_count=Count(
            "reviews",
            filter=Q(reviews__is_active=True, reviews__is_approved=True),
            distinct=True,
        ),
        average_rating=Avg(
            "reviews__rating",
            filter=Q(reviews__is_active=True, reviews__is_approved=True),
        ),
    )

    # Rating filter (après annotation)
    if rating in {"3", "4", "5"}:
        products_qs = products_qs.filter(average_rating__gte=int(rating))

    # Pagination
    paginator = Paginator(products_qs, 24)
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "categories": categories_qs,
        "current_category": current_category,
        "ecommerce_categories_nav": categories_qs[:30],
        "q": q,
        "category": category,
        "sort": sort,
        "badge": badge,
        "price_max": price_max if price_max is not None else max_price,
        "rating": rating,
        "max_price": max_price,
    }
    return render(request, template_name, context)


def ecommerce_index_view(request, category_slug=None):
    return _catalog_view(request, "economic/ecommerce/index.html", category_slug=category_slug)





# # economic/ecommerce/views/index.py
# from __future__ import annotations

# from decimal import Decimal, InvalidOperation

# from django.core.paginator import Paginator
# from django.core.exceptions import FieldDoesNotExist
# from django.db.models import Avg, Count, Max, Q
# from django.shortcuts import render

# from ..models.product import Product
# from ..models.category import Category


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _safe_decimal(value, default=None):
#     if value in (None, ""):
#         return default
#     try:
#         return Decimal(str(value))
#     except (InvalidOperation, TypeError, ValueError):
#         return default


# def _get_category_by_slug(language: str, slug_value: str):
#     """
#     Supporte 2 cas :
#     - slug est un champ traduit Parler (CategoryTranslation.slug)
#     - slug est un champ normal (Category.slug)
#     """
#     slug_value = (slug_value or "").strip()
#     if not slug_value:
#         return None

#     # 1) ✅ Cas Parler (slug traduit)
#     try:
#         return Category.objects.translated(language, slug=slug_value).get(is_active=True)
#     except Exception:
#         pass

#     # 2) ✅ Fallback explicite sur translations
#     try:
#         return Category.objects.filter(
#             is_active=True,
#             translations__language_code=language,
#             translations__slug=slug_value,
#         ).get()
#     except Exception:
#         pass

#     # 3) ✅ Dernier fallback : n'importe quelle langue
#     try:
#         return (
#             Category.objects.filter(is_active=True, translations__slug=slug_value)
#             .distinct()
#             .first()
#         )
#     except Exception:
#         return None


# def _catalog_view(request, template_name: str, category_slug=None):
#     language = request.LANGUAGE_CODE or "fr"

#     # Base QS
#     products_qs = (
#         Product.objects.filter(is_active=True)
#         .translated(language)
#         .select_related("category", "vendor")
#     )
#     categories_qs = Category.objects.filter(is_active=True).translated(language)

#     q = (request.GET.get("q") or "").strip()
#     sort = (request.GET.get("sort") or "").strip()
#     badge = (request.GET.get("badge") or "").strip()
#     category = (request.GET.get("category") or "").strip()
#     price_max = _safe_decimal(request.GET.get("price_max"))
#     rating = (request.GET.get("rating") or "").strip()
#     page_number = request.GET.get("page") or 1

#     current_category = None

#     # ✅ Category filter: URL takes priority
#     if category_slug:
#         current_category = _get_category_by_slug(language, category_slug)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)
#             category = category_slug
#     elif category:
#         current_category = _get_category_by_slug(language, category)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)

#     # Search
#     if q:
#         products_qs = products_qs.filter(translations__name__icontains=q).distinct()

#     # Max price for slider / UI
#     max_price = products_qs.aggregate(max_price=Max("price"))["max_price"] or Decimal("0")

#     if price_max is not None:
#         products_qs = products_qs.filter(price__lte=price_max)

#     # Rating filter (si annotations)
#     if rating in {"3", "4", "5"}:
#         # On peut filtrer après annotation (ci-dessous), mais safe ici si champ existe
#         if _has_field(Product, "average_rating"):
#             products_qs = products_qs.filter(average_rating__gte=int(rating))

#     # Badges / “options” cliquables
#     if badge == "fast" and _has_field(Product, "fast_delivery"):
#         products_qs = products_qs.filter(fast_delivery=True)

#     if badge == "choice" and _has_field(Product, "is_featured"):
#         products_qs = products_qs.filter(is_featured=True)

#     # Sorting
#     if sort == "new":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "best":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "price_asc":
#         products_qs = products_qs.order_by("price")
#     elif sort == "price_desc":
#         products_qs = products_qs.order_by("-price")
#     elif sort == "deals" and _has_field(Product, "is_featured"):
#         products_qs = products_qs.filter(is_featured=True).order_by("-created_at")

#     # ✅ Stats réelles: rating + reviews (Review.is_active & is_approved)
#     # (Review a related_name="reviews")
#     products_qs = products_qs.annotate(
#         reviews_count=Count(
#             "reviews",
#             filter=Q(reviews__is_active=True, reviews__is_approved=True),
#             distinct=True,
#         ),
#         average_rating=Avg(
#             "reviews__rating",
#             filter=Q(reviews__is_active=True, reviews__is_approved=True),
#         ),
#     )

#     # Pagination
#     paginator = Paginator(products_qs, 24)
#     page_obj = paginator.get_page(page_number)

#     context = {
#         "products": page_obj.object_list,
#         "page_obj": page_obj,
#         "is_paginated": page_obj.has_other_pages(),
#         "categories": categories_qs,
#         "current_category": current_category,
#         "ecommerce_categories_nav": categories_qs[:30],
#         "q": q,
#         "category": category,
#         "sort": sort,
#         "badge": badge,
#         "price_max": price_max if price_max is not None else max_price,
#         "rating": rating,
#         "max_price": max_price,
#     }
#     return render(request, template_name, context)


# def ecommerce_index_view(request, category_slug=None):
#     return _catalog_view(request, "economic/ecommerce/index.html", category_slug=category_slug)




# # economic/ecommerce/views/index.py
# from __future__ import annotations

# from decimal import Decimal, InvalidOperation

# from django.core.paginator import Paginator
# from django.core.exceptions import FieldDoesNotExist
# from django.db.models import Max, Avg, Count, Q
# from django.shortcuts import render

# from ..models.product import Product
# from ..models.category import Category


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _safe_decimal(value, default=None):
#     if value in (None, ""):
#         return default
#     try:
#         return Decimal(str(value))
#     except (InvalidOperation, TypeError, ValueError):
#         return default


# def _get_category_by_slug(language: str, slug_value: str):
#     """
#     Supporte 2 cas :
#     - slug est un champ traduit Parler (CategoryTranslation.slug)
#     - slug est un champ normal (Category.slug)
#     """
#     slug_value = (slug_value or "").strip()
#     if not slug_value:
#         return None

#     # 1) ✅ Cas Parler (slug traduit)
#     try:
#         return Category.objects.translated(language, slug=slug_value).get(is_active=True)
#     except Exception:
#         pass

#     # 2) ✅ Fallback explicite sur translations
#     try:
#         return Category.objects.filter(
#             is_active=True,
#             translations__language_code=language,
#             translations__slug=slug_value,
#         ).get()
#     except Exception:
#         pass

#     # 3) ✅ Dernier fallback : n'importe quelle langue
#     try:
#         return (
#             Category.objects.filter(is_active=True, translations__slug=slug_value)
#             .distinct()
#             .first()
#         )
#     except Exception:
#         return None


# def _compute_promo_fields_for_list(products):
#     """
#     ✅ Ajoute des attributs runtime (pas DB) :
#       - effective_price
#       - old_price_display
#       - has_promo
#       - discount_percent
#     Stratégie:
#       - si product.promo_price existe => promo
#       - sinon si product.old_price existe (champ DB) => promo
#       - sinon => pas promo
#     """
#     for p in products:
#         # base price
#         try:
#             base = Decimal(str(getattr(p, "price", None) or "0"))
#         except Exception:
#             base = Decimal("0")

#         promo = None

#         # 1) promo_price (si ton modèle/pricing l'expose)
#         if hasattr(p, "promo_price"):
#             try:
#                 v = getattr(p, "promo_price", None)
#                 if v not in (None, ""):
#                     promo = Decimal(str(v))
#             except Exception:
#                 promo = None

#         # 2) old_price (SEULEMENT si la colonne existe vraiment)
#         #    => ici on ne force jamais une colonne DB inexistante
#         old_db = None
#         if hasattr(p, "old_price"):
#             try:
#                 v = getattr(p, "old_price", None)
#                 if v not in (None, ""):
#                     old_db = Decimal(str(v))
#             except Exception:
#                 old_db = None

#         # Si old_price existe et est > price => on considère promo
#         if promo is None and old_db is not None and old_db > base:
#             promo = base
#             base = old_db  # old_db devient le "prix barré"

#         has_promo = bool(promo is not None and base > 0 and promo < base)

#         if has_promo:
#             pct = int(round(((base - promo) * Decimal("100")) / base))
#             pct = max(1, min(pct, 95))
#             p.has_promo = True
#             p.effective_price = promo
#             p.old_price_display = base
#             p.discount_percent = pct
#         else:
#             p.has_promo = False
#             p.effective_price = base
#             p.old_price_display = None
#             p.discount_percent = 0

#     return products


# def _catalog_view(request, template_name: str, category_slug=None):
#     language = request.LANGUAGE_CODE or "fr"

#     # ✅ base existant
#     products_qs = Product.objects.filter(is_active=True).translated(language)
#     categories_qs = Category.objects.filter(is_active=True).translated(language)

#     q = (request.GET.get("q") or "").strip()
#     sort = (request.GET.get("sort") or "").strip()
#     badge = (request.GET.get("badge") or "").strip()
#     category = (request.GET.get("category") or "").strip()
#     price_max = _safe_decimal(request.GET.get("price_max"))
#     rating = (request.GET.get("rating") or "").strip()
#     page_number = request.GET.get("page") or 1

#     current_category = None

#     # ✅ Category filter: URL takes priority
#     if category_slug:
#         current_category = _get_category_by_slug(language, category_slug)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)
#             category = category_slug
#     elif category:
#         current_category = _get_category_by_slug(language, category)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)

#     # Search
#     if q:
#         products_qs = products_qs.filter(translations__name__icontains=q).distinct()

#     # ✅ max_price sur price (comme avant)
#     max_price = products_qs.aggregate(max_price=Max("price"))["max_price"] or Decimal("0")

#     if price_max is not None:
#         products_qs = products_qs.filter(price__lte=price_max)

#     # ✅ Reviews: toujours safe (tu as review.py avec related_name="reviews")
#     products_qs = products_qs.annotate(
#         average_rating=Avg(
#             "reviews__rating",
#             filter=Q(reviews__is_active=True, reviews__is_approved=True),
#         ),
#         reviews_count=Count(
#             "reviews",
#             filter=Q(reviews__is_active=True, reviews__is_approved=True),
#             distinct=True,
#         ),
#     )

#     # rating filter (sur annotation)
#     if rating in {"3", "4", "5"}:
#         products_qs = products_qs.filter(average_rating__gte=int(rating))

#     # badge filter (safe)
#     if badge == "fast" and _has_field(Product, "fast_delivery"):
#         products_qs = products_qs.filter(fast_delivery=True)

#     # sort (comme avant)
#     if sort == "new":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "best":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "price_asc":
#         products_qs = products_qs.order_by("price")
#     elif sort == "price_desc":
#         products_qs = products_qs.order_by("-price")
#     elif sort == "deals" and _has_field(Product, "is_featured"):
#         products_qs = products_qs.filter(is_featured=True).order_by("-created_at")

#     paginator = Paginator(products_qs, 24)
#     page_obj = paginator.get_page(page_number)

#     # ✅ IMPORTANT: on enrichit juste les objets affichés (runtime)
#     products_list = list(page_obj.object_list)
#     products_list = _compute_promo_fields_for_list(products_list)
#     page_obj.object_list = products_list  # pour templates

#     context = {
#         "products": page_obj.object_list,
#         "page_obj": page_obj,
#         "is_paginated": page_obj.has_other_pages(),

#         "categories": categories_qs,
#         "current_category": current_category,
#         "ecommerce_categories_nav": categories_qs[:30],

#         "q": q,
#         "category": category,
#         "sort": sort,
#         "badge": badge,
#         "price_max": price_max if price_max is not None else max_price,
#         "rating": rating,

#         "max_price": max_price,
#     }
#     return render(request, template_name, context)


# def ecommerce_index_view(request, category_slug=None):
#     return _catalog_view(request, "economic/ecommerce/index.html", category_slug=category_slug)





# # economic/ecommerce/views/index.py
# from decimal import Decimal, InvalidOperation

# from django.core.paginator import Paginator
# from django.db.models import Max
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import render, get_object_or_404

# from ..models.product import Product
# from ..models.category import Category


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _safe_decimal(value, default=None):
#     if value in (None, ""):
#         return default
#     try:
#         return Decimal(str(value))
#     except (InvalidOperation, TypeError, ValueError):
#         return default


# def _get_category_by_slug(language: str, slug_value: str):
#     """
#     Supporte 2 cas :
#     - slug est un champ traduit Parler (CategoryTranslation.slug)
#     - slug est un champ normal (Category.slug)
#     """
#     slug_value = (slug_value or "").strip()
#     if not slug_value:
#         return None

#     # 1) ✅ Cas Parler (slug traduit) — la meilleure façon
#     try:
#         return Category.objects.translated(language, slug=slug_value).get(is_active=True)
#     except Exception:
#         pass

#     # 2) ✅ Fallback explicite sur la table translations
#     try:
#         return Category.objects.filter(
#             is_active=True,
#             translations__language_code=language,
#             translations__slug=slug_value,
#         ).get()
#     except Exception:
#         pass

#     # 3) ✅ Dernier fallback : n'importe quelle langue (utile si URL copiée)
#     try:
#         return Category.objects.filter(
#             is_active=True,
#             translations__slug=slug_value,
#         ).distinct().first()
#     except Exception:
#         return None


# def _catalog_view(request, template_name: str, category_slug=None):
#     language = request.LANGUAGE_CODE or "fr"

#     products_qs = Product.objects.filter(is_active=True).translated(language)
#     categories_qs = Category.objects.filter(is_active=True).translated(language)

#     q = (request.GET.get("q") or "").strip()
#     sort = (request.GET.get("sort") or "").strip()
#     badge = (request.GET.get("badge") or "").strip()
#     category = (request.GET.get("category") or "").strip()
#     price_max = _safe_decimal(request.GET.get("price_max"))
#     rating = (request.GET.get("rating") or "").strip()
#     page_number = request.GET.get("page") or 1

#     current_category = None

#     # ✅ Category filter: URL takes priority
#     if category_slug:
#         current_category = _get_category_by_slug(language, category_slug)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)
#             category = category_slug
#     elif category:
#         current_category = _get_category_by_slug(language, category)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)

#     # Search
#     if q:
#         products_qs = products_qs.filter(translations__name__icontains=q).distinct()

#     max_price = products_qs.aggregate(max_price=Max("price"))["max_price"] or Decimal("0")

#     if price_max is not None:
#         products_qs = products_qs.filter(price__lte=price_max)

#     if rating in {"3", "4", "5"} and _has_field(Product, "average_rating"):
#         products_qs = products_qs.filter(average_rating__gte=int(rating))

#     if badge == "fast" and _has_field(Product, "fast_delivery"):
#         products_qs = products_qs.filter(fast_delivery=True)

#     if sort == "new":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "best":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "price_asc":
#         products_qs = products_qs.order_by("price")
#     elif sort == "price_desc":
#         products_qs = products_qs.order_by("-price")
#     elif sort == "deals" and _has_field(Product, "is_featured"):
#         products_qs = products_qs.filter(is_featured=True).order_by("-created_at")

#     paginator = Paginator(products_qs, 24)
#     page_obj = paginator.get_page(page_number)

#     context = {
#         "products": page_obj.object_list,
#         "page_obj": page_obj,
#         "is_paginated": page_obj.has_other_pages(),

#         "categories": categories_qs,
#         "current_category": current_category,
#         "ecommerce_categories_nav": categories_qs[:30],

#         "q": q,
#         "category": category,
#         "sort": sort,
#         "badge": badge,
#         "price_max": price_max if price_max is not None else max_price,
#         "rating": rating,

#         "max_price": max_price,
#     }
#     return render(request, template_name, context)


# def ecommerce_index_view(request, category_slug=None):
#     return _catalog_view(request, "economic/ecommerce/index.html", category_slug=category_slug)








# # economic/ecommerce/views/index.py
# from decimal import Decimal, InvalidOperation

# from django.core.paginator import Paginator
# from django.db.models import Max
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import render, get_object_or_404

# from ..models.product import Product
# from ..models.category import Category


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _safe_decimal(value, default=None):
#     if value in (None, ""):
#         return default
#     try:
#         return Decimal(str(value))
#     except (InvalidOperation, TypeError, ValueError):
#         return default


# def _get_category_by_slug(language: str, slug_value: str):
#     """
#     Supporte 2 cas :
#     - slug est un champ traduit Parler (CategoryTranslation.slug)
#     - slug est un champ normal (Category.slug)
#     """
#     slug_value = (slug_value or "").strip()
#     if not slug_value:
#         return None

#     # 1) ✅ Cas Parler (slug traduit) — la meilleure façon
#     try:
#         return Category.objects.translated(language, slug=slug_value).get(is_active=True)
#     except Exception:
#         pass

#     # 2) ✅ Fallback explicite sur la table translations
#     try:
#         return Category.objects.filter(
#             is_active=True,
#             translations__language_code=language,
#             translations__slug=slug_value,
#         ).get()
#     except Exception:
#         pass

#     # 3) ✅ Dernier fallback : n'importe quelle langue (utile si URL copiée)
#     try:
#         return Category.objects.filter(
#             is_active=True,
#             translations__slug=slug_value,
#         ).distinct().first()
#     except Exception:
#         return None


# def _catalog_view(request, template_name: str, category_slug=None):
#     language = request.LANGUAGE_CODE or "fr"

#     products_qs = Product.objects.filter(is_active=True).translated(language)
#     categories_qs = Category.objects.filter(is_active=True).translated(language)

#     q = (request.GET.get("q") or "").strip()
#     sort = (request.GET.get("sort") or "").strip()
#     badge = (request.GET.get("badge") or "").strip()
#     category = (request.GET.get("category") or "").strip()
#     price_max = _safe_decimal(request.GET.get("price_max"))
#     rating = (request.GET.get("rating") or "").strip()
#     page_number = request.GET.get("page") or 1

#     current_category = None

#     # ✅ Category filter: URL takes priority
#     if category_slug:
#         current_category = _get_category_by_slug(language, category_slug)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)
#             category = category_slug
#     elif category:
#         current_category = _get_category_by_slug(language, category)
#         if current_category:
#             products_qs = products_qs.filter(category=current_category)

#     # Search
#     if q:
#         products_qs = products_qs.filter(translations__name__icontains=q).distinct()

#     max_price = products_qs.aggregate(max_price=Max("price"))["max_price"] or Decimal("0")

#     if price_max is not None:
#         products_qs = products_qs.filter(price__lte=price_max)

#     if rating in {"3", "4", "5"} and _has_field(Product, "average_rating"):
#         products_qs = products_qs.filter(average_rating__gte=int(rating))

#     if badge == "fast" and _has_field(Product, "fast_delivery"):
#         products_qs = products_qs.filter(fast_delivery=True)

#     if sort == "new":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "best":
#         products_qs = products_qs.order_by("-created_at")
#     elif sort == "price_asc":
#         products_qs = products_qs.order_by("price")
#     elif sort == "price_desc":
#         products_qs = products_qs.order_by("-price")
#     elif sort == "deals" and _has_field(Product, "is_featured"):
#         products_qs = products_qs.filter(is_featured=True).order_by("-created_at")

#     paginator = Paginator(products_qs, 24)
#     page_obj = paginator.get_page(page_number)

#     context = {
#         "products": page_obj.object_list,
#         "page_obj": page_obj,
#         "is_paginated": page_obj.has_other_pages(),

#         "categories": categories_qs,
#         "current_category": current_category,
#         "ecommerce_categories_nav": categories_qs[:30],

#         "q": q,
#         "category": category,
#         "sort": sort,
#         "badge": badge,
#         "price_max": price_max if price_max is not None else max_price,
#         "rating": rating,

#         "max_price": max_price,
#     }
#     return render(request, template_name, context)


# def ecommerce_index_view(request, category_slug=None):
#     return _catalog_view(request, "economic/ecommerce/index.html", category_slug=category_slug)





# # economic/ecommerce/views/index.py

# from decimal import Decimal

# from django.core.paginator import Paginator
# from django.db.models import Q, Max
# from django.shortcuts import render
# from django.utils.translation import gettext as _

# from parler.utils.context import switch_language  # si tu veux l'utiliser ailleurs
# from ..models.product import Product
# from ..models.category import Category


# def ecommerce_index_view(request, category_slug=None):
#     """
#     Catalogue principal des produits (page boutique).

#     - Compatible Django-Parler (langue courante)
#     - Gère :
#         * recherche (q)
#         * filtre catégorie (URL ou ?category=)
#         * filtre prix max (?price_max=)
#         * filtre rating (?rating=)
#         * tri (?sort=price_asc / price_desc / new / best)
#         * pagination
#     - Context compatible avec templates :
#         economic/ecommerce/index.html
#         economic/ecommerce/product_list.html
#         economic/ecommerce/search.html
#     """
#     # Langue courante pour Parler
#     language = request.LANGUAGE_CODE or "fr"

#     # ============================
#     #  BASE QUERYSET TRADUIT
#     # ============================
#     products = Product.objects.filter(is_active=True).translated(language)
#     categories = Category.objects.filter(is_active=True).translated(language)

#     # ============================
#     #  CATÉGORIE (URL ou GET)
#     # ============================
#     # 1) cat via URL : /boutique/<slug>/
#     current_category_slug = category_slug

#     # 2) ou via ?category=… si pas de slug en URL
#     if not current_category_slug:
#         current_category_slug = request.GET.get("category") or ""

#     current_category = None
#     if current_category_slug:
#         try:
#             current_category = (
#                 Category.objects
#                 .translated(language)
#                 .get(slug=current_category_slug, is_active=True)
#             )
#             products = products.filter(category=current_category)
#         except Category.DoesNotExist:
#             current_category = None

#     # ============================
#     #  PRIX MAX GLOBAL (AVANT FILTRES PRIX)
#     # ============================
#     max_price_global = (
#         products.aggregate(max_price=Max("price")).get("max_price")
#         or Decimal("0")
#     )

#     # ============================
#     #  AUTRES FILTRES & TRI
#     # ============================
#     q = (request.GET.get("q") or "").strip()
#     sort = request.GET.get("sort") or ""
#     price_max_param = request.GET.get("price_max") or ""
#     rating = request.GET.get("rating") or ""

#     # Recherche texte
#     if q:
#         products = products.filter(
#             Q(translations__name__icontains=q)
#             | Q(translations__description__icontains=q)
#         ).distinct()

#     # Filtre prix max
#     if price_max_param:
#         try:
#             price_limit = Decimal(price_max_param)
#         except Exception:
#             price_limit = max_price_global
#     else:
#         price_limit = max_price_global

#     if price_limit and price_limit > 0:
#         products = products.filter(price__lte=price_limit)

#     # Filtre rating (si tu as average_rating sur Product)
#     if rating:
#         try:
#             rating_val = float(rating)
#             products = products.filter(average_rating__gte=rating_val)
#         except Exception:
#             # si mauvaise valeur ou pas de champ, on ignore
#             pass

#     # Tri
#     if sort == "price_asc":
#         products = products.order_by("price")
#     elif sort == "price_desc":
#         products = products.order_by("-price")
#     elif sort == "new":
#         # adapte le champ si différent
#         products = products.order_by("-created_at")
#     elif sort == "best":
#         # si tu as un champ sales_count, utilise-le
#         if hasattr(Product, "sales_count"):
#             products = products.order_by("-sales_count")

#     # ============================
#     #  PAGINATION
#     # ============================
#     paginator = Paginator(products, 24)  # 24 produits par page
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     # ============================
#     #  CONTEXTE POUR LES TEMPLATES
#     # ============================
#     context = {
#         # data principale
#         "products": page_obj.object_list,
#         "page_obj": page_obj,
#         "is_paginated": page_obj.has_other_pages(),

#         # catégories / sélection
#         "categories": categories,
#         "current_category": current_category,

#         # filtres pour réaffichage form / liens
#         "q": q,
#         "category": current_category_slug,
#         "sort": sort,
#         "price_max": price_limit,
#         "rating": rating,
#         "max_price": max_price_global,
#     }

#     return render(request, "economic/ecommerce/index.html", context)



# # economic/ecommerce/views/index.py
# from django.shortcuts import render
# from django.db.models import Max
# from parler.utils.context import switch_language

# from ..models.product import Product
# from ..models.category import Category


# def ecommerce_index_view(request, category_slug=None):
#     """
#     Catalogue principal des produits
#     Compatible Django-Parler (langue courante)
#     """
#     language = request.LANGUAGE_CODE

#     products = Product.objects.filter(is_active=True).translated(language)
#     categories = Category.objects.filter(is_active=True).translated(language)

#     current_category = None
#     if category_slug:
#         current_category = Category.objects.translated(language).get(slug=category_slug)
#         products = products.filter(category=current_category)

#     # ✅ CORRECTION : prix maximum réel
#     max_price = products.aggregate(max_price=Max("price"))["max_price"] or 0

#     context = {
#         "products": products,
#         "categories": categories,
#         "current_category": current_category,
#         "max_price": max_price,  # 🔑 FIX
#     }

#     return render(request, "economic/ecommerce/index.html", context)








# # economic/ecommerce/views/index.py
# from django.shortcuts import render
# from parler.utils.context import switch_language

# from ..models.product import Product
# from ..models.category import Category


# def ecommerce_index_view(request, category_slug=None):
#     """
#     Catalogue principal des produits
#     Compatible Parler (langue courante)
#     """
#     language = request.LANGUAGE_CODE

#     products = Product.objects.filter(is_active=True).translated(language)
#     categories = Category.objects.filter(is_active=True).translated(language)

#     current_category = None
#     if category_slug:
#         current_category = Category.objects.translated(language).get(slug=category_slug)
#         products = products.filter(category=current_category)

#     context = {
#         "products": products,
#         "categories": categories,
#         "current_category": current_category,
#     }
#     return render(request, "economic/ecommerce/index.html", context)
