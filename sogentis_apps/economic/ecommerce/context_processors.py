# economic/ecommerce/context_processors.py
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Count

def ecommerce_context(request):
    """
    E-commerce UI:
      - catégories dropdown
      - uuid tracking pré-rempli
    """
    categories_nav = []
    try:
        from .models.category import Category
        language = getattr(request, "LANGUAGE_CODE", None) or "fr"
        categories_nav = (
            Category.objects.filter(is_active=True)
            .translated(language)
            .order_by("translations__name")[:50]
        )
    except (OperationalError, ProgrammingError, Exception):
        categories_nav = []

    return {
        "ecommerce_categories_nav": categories_nav,
        "track_default": (request.GET.get("track") or "").strip(),
    }


def _count_cart_items_session(request) -> int:
    """
    Fallback panier session.
    Supporte:
      - cart = dict {product_id: {"qty": 2}}  ou {product_id: 2}
      - cart = list d'items
    """
    cart = request.session.get("cart") or request.session.get("CART") or {}
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

    return max(total, 0)


def _count_cart_items_db(request) -> int:
    """
    Panier DB-safe:
      - essaie economic.ecommerce.models.cart.Cart
      - essaie cart.items.count() ou somme item.quantity
    """
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated):
        return 0

    try:
        from economic.ecommerce.models.cart import Cart  # adapte si ton chemin diffère
    except Exception:
        return 0

    try:
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            return 0

        # 1) si items est un related_name
        items_rel = getattr(cart, "items", None)
        if items_rel is None:
            return 0

        # si tu as quantity
        try:
            total = items_rel.aggregate(n=Count("id")).get("n") or 0
            # si tu veux somme qty (si champ existe)
            # total = sum(int(i.quantity or 0) for i in items_rel.all())
            return int(total)
        except Exception:
            try:
                return int(items_rel.count())
            except Exception:
                return 0

    except (OperationalError, ProgrammingError, Exception):
        return 0


def ecommerce_counts(request):
    """
    Injecte partout:
      - favorites_count
      - cart_items_count (DB si possible, sinon session)
    """
    favorites_count = 0
    cart_items_count = 0

    user = getattr(request, "user", None)

    # ✅ Favoris (DB)
    if user and user.is_authenticated:
        try:
            from .models.favorite import Favorite
            favorites_count = (
                Favorite.objects.filter(user=user)
                .aggregate(n=Count("id"))
                .get("n") or 0
            )
        except (OperationalError, ProgrammingError, Exception):
            favorites_count = 0

    # ✅ Panier (DB -> fallback session)
    cart_items_count = _count_cart_items_db(request)
    if not cart_items_count:
        cart_items_count = _count_cart_items_session(request)

    # ✅ utile : on garde aussi une copie en session (optim perf + affichage stable)
    try:
        request.session["cart_items_count"] = int(cart_items_count)
        request.session.modified = True
    except Exception:
        pass

    return {
        "favorites_count": int(favorites_count or 0),
        "cart_items_count": int(cart_items_count or 0),
    }
