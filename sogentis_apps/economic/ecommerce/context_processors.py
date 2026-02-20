# economic/ecommerce/context_processors.py
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Sum
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)


# ----------------------------
# NAV (catégories)
# ----------------------------
def ecommerce_context(request) -> dict[str, Any]:
    categories_nav = []
    language = getattr(request, "LANGUAGE_CODE", None) or "fr"
    lang2 = (language or "fr")[:2].lower()

    cache_key = f"ecom:categories_nav:{lang2}"
    cache_ttl = getattr(settings, "ECOMMERCE_CATEGORIES_NAV_TTL", 300)  # 5 min

    try:
        cached = cache.get(cache_key)
        if cached is not None:
            categories_nav = cached
        else:
            from .models.category import Category  # local import (safe)

            qs = (
                Category.objects.filter(is_active=True)
                .translated(language_code=language)  # parler-safe
                .order_by("translations__name")[:50]
            )
            categories_nav = list(qs)
            cache.set(cache_key, categories_nav, cache_ttl)
    except (OperationalError, ProgrammingError) as e:
        logger.debug("ecommerce_context categories unavailable: %s", e)
        categories_nav = []
    except Exception as e:
        logger.warning("ecommerce_context categories error: %s", e, exc_info=False)
        categories_nav = []

    return {
        "ecommerce_categories_nav": categories_nav,
        "track_default": (request.GET.get("track") or "").strip(),
    }


# ----------------------------
# CART COUNT (session)
# ----------------------------
def _cart_session_keys() -> list[str]:
    # ✅ override possible dans settings
    keys = getattr(settings, "ECOMMERCE_CART_SESSION_KEYS", None)
    if isinstance(keys, (list, tuple)) and keys:
        return [str(k) for k in keys]
    return ["ECOMMERCE_CART", "ecommerce_cart", "cart", "CART"]


def _get_cart_from_session(request) -> Any:
    for k in _cart_session_keys():
        if k in request.session:
            return request.session.get(k)
    return {}


def _count_cart_items_session(request) -> int:
    cart = _get_cart_from_session(request)
    total = 0

    try:
        if isinstance(cart, dict):
            for _, v in cart.items():
                if isinstance(v, dict):
                    total += int(v.get("qty") or v.get("quantity") or 0)
                else:
                    total += int(v or 0)
        elif isinstance(cart, list):
            for item in cart:
                if isinstance(item, dict):
                    total += int(item.get("qty") or item.get("quantity") or 0)
                else:
                    total += 1
    except Exception:
        total = 0

    return max(int(total), 0)


# ----------------------------
# CART COUNT (DB)
# ----------------------------
def _count_cart_items_db(request) -> int:
    user = getattr(request, "user", None)
    if not (user and getattr(user, "is_authenticated", False)):
        return 0

    try:
        from economic.ecommerce.models.cart import Cart
    except Exception:
        return 0

    try:
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            return 0

        items_rel = getattr(cart, "items", None)
        if items_rel is None:
            return 0

        # ✅ somme qty si existe
        try:
            s = items_rel.aggregate(s=Sum("quantity")).get("s")
            if s is not None:
                return max(int(s or 0), 0)
        except Exception:
            pass

        # fallback count
        try:
            n = items_rel.aggregate(n=Count("id")).get("n") or 0
            return max(int(n), 0)
        except Exception:
            try:
                return max(int(items_rel.count()), 0)
            except Exception:
                return 0

    except (OperationalError, ProgrammingError):
        return 0
    except Exception:
        return 0


# ----------------------------
# COUNTS (navbar)
# ----------------------------
def ecommerce_counts(request) -> dict[str, int]:
    favorites_count = 0
    cart_items_count = 0

    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        try:
            from .models.favorite import Favorite
            favorites_count = Favorite.objects.filter(user=user).count()
        except (OperationalError, ProgrammingError):
            favorites_count = 0
        except Exception:
            favorites_count = 0

    # ✅ DB -> session (fallback)
    cart_items_count = _count_cart_items_db(request)
    if cart_items_count <= 0:
        cart_items_count = _count_cart_items_session(request)

    return {
        "favorites_count": int(favorites_count or 0),
        "cart_items_count": int(cart_items_count or 0),
    }







# # economic/ecommerce/context_processors.py
# from __future__ import annotations

# from django.db.models import Count, Sum
# from django.db.utils import OperationalError, ProgrammingError


# def ecommerce_context(request):
#     categories_nav = []
#     try:
#         from .models.category import Category

#         language = getattr(request, "LANGUAGE_CODE", None) or "fr"
#         categories_nav = (
#             Category.objects.filter(is_active=True)
#             .translated(language)
#             .order_by("translations__name")[:50]
#         )
#     except (OperationalError, ProgrammingError, Exception):
#         categories_nav = []

#     return {
#         "ecommerce_categories_nav": categories_nav,
#         "track_default": (request.GET.get("track") or "").strip(),
#     }


# def _count_cart_items_session(request) -> int:
#     # ✅ IMPORTANT: on supporte TA clé session réelle
#     cart = (
#         request.session.get("ECOMMERCE_CART")
#         or request.session.get("ecommerce_cart")
#         or request.session.get("cart")
#         or request.session.get("CART")
#         or {}
#     )

#     total = 0
#     try:
#         if isinstance(cart, dict):
#             for _, v in cart.items():
#                 if isinstance(v, dict):
#                     total += int(v.get("qty") or v.get("quantity") or 0)
#                 else:
#                     total += int(v or 0)
#         elif isinstance(cart, list):
#             for item in cart:
#                 if isinstance(item, dict):
#                     total += int(item.get("qty") or item.get("quantity") or 0)
#                 else:
#                     total += 1
#     except Exception:
#         total = 0

#     return max(int(total), 0)


# def _count_cart_items_db(request) -> int:
#     user = getattr(request, "user", None)
#     if not (user and user.is_authenticated):
#         return 0

#     try:
#         from economic.ecommerce.models.cart import Cart
#     except Exception:
#         return 0

#     try:
#         cart = Cart.objects.filter(user=user).first()
#         if not cart:
#             return 0

#         items_rel = getattr(cart, "items", None)
#         if items_rel is None:
#             return 0

#         # ✅ somme qty si existe
#         try:
#             s = items_rel.aggregate(s=Sum("quantity")).get("s")
#             if s is not None:
#                 return max(int(s or 0), 0)
#         except Exception:
#             pass

#         # fallback count
#         try:
#             n = items_rel.aggregate(n=Count("id")).get("n") or 0
#             return max(int(n), 0)
#         except Exception:
#             try:
#                 return max(int(items_rel.count()), 0)
#             except Exception:
#                 return 0

#     except (OperationalError, ProgrammingError, Exception):
#         return 0


# def ecommerce_counts(request):
#     favorites_count = 0
#     cart_items_count = 0

#     user = getattr(request, "user", None)

#     if user and user.is_authenticated:
#         try:
#             from .models.favorite import Favorite

#             favorites_count = Favorite.objects.filter(user=user).count()
#         except (OperationalError, ProgrammingError, Exception):
#             favorites_count = 0

#     # ✅ DB -> session
#     cart_items_count = _count_cart_items_db(request)
#     if cart_items_count <= 0:
#         cart_items_count = _count_cart_items_session(request)

#     # ✅ DEBUG TEMP (retire après test): expose les clés trouvées
#     try:
#         request.session["__cart_debug_keys__"] = [
#             k for k in ["ECOMMERCE_CART", "ecommerce_cart", "cart", "CART"] if k in request.session
#         ]
#         request.session["__cart_debug_sample__"] = (
#             request.session.get("ECOMMERCE_CART")
#             or request.session.get("ecommerce_cart")
#             or request.session.get("cart")
#             or request.session.get("CART")
#             or None
#         )
#         request.session.modified = True
#     except Exception:
#         pass

#     return {
#         "favorites_count": int(favorites_count or 0),
#         "cart_items_count": int(cart_items_count or 0),
#     }






# # economic/ecommerce/context_processors.py
# from django.db.utils import OperationalError, ProgrammingError
# from django.db.models import Count

# def ecommerce_context(request):
#     """
#     E-commerce UI:
#       - catégories dropdown
#       - uuid tracking pré-rempli
#     """
#     categories_nav = []
#     try:
#         from .models.category import Category
#         language = getattr(request, "LANGUAGE_CODE", None) or "fr"
#         categories_nav = (
#             Category.objects.filter(is_active=True)
#             .translated(language)
#             .order_by("translations__name")[:50]
#         )
#     except (OperationalError, ProgrammingError, Exception):
#         categories_nav = []

#     return {
#         "ecommerce_categories_nav": categories_nav,
#         "track_default": (request.GET.get("track") or "").strip(),
#     }


# def _count_cart_items_session(request) -> int:
#     """
#     Fallback panier session.
#     Supporte:
#       - cart = dict {product_id: {"qty": 2}}  ou {product_id: 2}
#       - cart = list d'items
#     """
#     cart = request.session.get("cart") or request.session.get("CART") or {}
#     total = 0

#     try:
#         if isinstance(cart, dict):
#             for _, v in cart.items():
#                 if isinstance(v, dict):
#                     total += int(v.get("qty") or v.get("quantity") or 0)
#                 else:
#                     total += int(v or 0)
#         elif isinstance(cart, list):
#             for item in cart:
#                 if isinstance(item, dict):
#                     total += int(item.get("qty") or item.get("quantity") or 0)
#                 else:
#                     total += 1
#     except Exception:
#         total = 0

#     return max(total, 0)


# def _count_cart_items_db(request) -> int:
#     """
#     Panier DB-safe:
#       - essaie economic.ecommerce.models.cart.Cart
#       - essaie cart.items.count() ou somme item.quantity
#     """
#     user = getattr(request, "user", None)
#     if not (user and user.is_authenticated):
#         return 0

#     try:
#         from economic.ecommerce.models.cart import Cart  # adapte si ton chemin diffère
#     except Exception:
#         return 0

#     try:
#         cart = Cart.objects.filter(user=user).first()
#         if not cart:
#             return 0

#         # 1) si items est un related_name
#         items_rel = getattr(cart, "items", None)
#         if items_rel is None:
#             return 0

#         # si tu as quantity
#         try:
#             total = items_rel.aggregate(n=Count("id")).get("n") or 0
#             # si tu veux somme qty (si champ existe)
#             # total = sum(int(i.quantity or 0) for i in items_rel.all())
#             return int(total)
#         except Exception:
#             try:
#                 return int(items_rel.count())
#             except Exception:
#                 return 0

#     except (OperationalError, ProgrammingError, Exception):
#         return 0


# def ecommerce_counts(request):
#     """
#     Injecte partout:
#       - favorites_count
#       - cart_items_count (DB si possible, sinon session)
#     """
#     favorites_count = 0
#     cart_items_count = 0

#     user = getattr(request, "user", None)

#     # ✅ Favoris (DB)
#     if user and user.is_authenticated:
#         try:
#             from .models.favorite import Favorite
#             favorites_count = (
#                 Favorite.objects.filter(user=user)
#                 .aggregate(n=Count("id"))
#                 .get("n") or 0
#             )
#         except (OperationalError, ProgrammingError, Exception):
#             favorites_count = 0

#     # ✅ Panier (DB -> fallback session)
#     cart_items_count = _count_cart_items_db(request)
#     if not cart_items_count:
#         cart_items_count = _count_cart_items_session(request)

#     # ✅ utile : on garde aussi une copie en session (optim perf + affichage stable)
#     try:
#         request.session["cart_items_count"] = int(cart_items_count)
#         request.session.modified = True
#     except Exception:
#         pass

#     return {
#         "favorites_count": int(favorites_count or 0),
#         "cart_items_count": int(cart_items_count or 0),
#     }
