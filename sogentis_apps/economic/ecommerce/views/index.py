# economic/ecommerce/views/index.py
from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Max
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import render, get_object_or_404

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

    # 1) ✅ Cas Parler (slug traduit) — la meilleure façon
    try:
        return Category.objects.translated(language, slug=slug_value).get(is_active=True)
    except Exception:
        pass

    # 2) ✅ Fallback explicite sur la table translations
    try:
        return Category.objects.filter(
            is_active=True,
            translations__language_code=language,
            translations__slug=slug_value,
        ).get()
    except Exception:
        pass

    # 3) ✅ Dernier fallback : n'importe quelle langue (utile si URL copiée)
    try:
        return Category.objects.filter(
            is_active=True,
            translations__slug=slug_value,
        ).distinct().first()
    except Exception:
        return None


def _catalog_view(request, template_name: str, category_slug=None):
    language = request.LANGUAGE_CODE or "fr"

    products_qs = Product.objects.filter(is_active=True).translated(language)
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

    max_price = products_qs.aggregate(max_price=Max("price"))["max_price"] or Decimal("0")

    if price_max is not None:
        products_qs = products_qs.filter(price__lte=price_max)

    if rating in {"3", "4", "5"} and _has_field(Product, "average_rating"):
        products_qs = products_qs.filter(average_rating__gte=int(rating))

    if badge == "fast" and _has_field(Product, "fast_delivery"):
        products_qs = products_qs.filter(fast_delivery=True)

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
