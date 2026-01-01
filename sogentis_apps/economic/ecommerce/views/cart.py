# economic/ecommerce/views/cart.py
from dataclasses import dataclass
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from ..models.product import Product

CART_SESSION_KEY = "ecommerce_cart"


# =========================================================
#  BADGE COUNT (SESSION) — PROD SAFE
# =========================================================
def _count_cart_items_session(request) -> int:
    """
    Calcule le total d'articles (somme des quantités) dans le panier session.
    Structure: {"12": 2, "99": 1}
    """
    raw = request.session.get(CART_SESSION_KEY, {})
    total = 0
    if not isinstance(raw, dict):
        return 0

    for _, qty in raw.items():
        try:
            total += int(qty or 0)
        except (TypeError, ValueError):
            continue

    return max(total, 0)


def _sync_cart_badge_count(request) -> None:
    """
    Met à jour request.session['cart_items_count'] après chaque action panier.
    """
    try:
        request.session["cart_items_count"] = int(_count_cart_items_session(request))
        request.session.modified = True
    except Exception:
        pass


# =========================================================
#  CART ITEM (VIEW MODEL)
# =========================================================
@dataclass
class CartItem:
    product: Product
    quantity: int
    unit_price: Decimal

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


# =========================================================
#  SESSION HELPERS
# =========================================================
def _get_cart_raw(request) -> dict:
    data = request.session.get(CART_SESSION_KEY, {})
    return data if isinstance(data, dict) else {}


def _save_cart_raw(request, data: dict) -> None:
    request.session[CART_SESSION_KEY] = data
    request.session.modified = True
    _sync_cart_badge_count(request)  # ✅ badge sync ici


def _build_cart_items(request):
    raw = _get_cart_raw(request)

    product_ids = []
    for pid in raw.keys():
        try:
            product_ids.append(int(pid))
        except ValueError:
            continue

    products = Product.objects.filter(id__in=product_ids, is_active=True)
    products_by_id = {p.id: p for p in products}

    items: list[CartItem] = []
    total = Decimal("0.00")

    for pid_str, qty in raw.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue

        product = products_by_id.get(pid)
        if not product:
            continue

        try:
            quantity = int(qty)
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        unit_price = getattr(product, "price", None) or Decimal("0.00")
        try:
            unit_price = Decimal(str(unit_price))
        except Exception:
            unit_price = Decimal("0.00")

        item = CartItem(product=product, quantity=quantity, unit_price=unit_price)
        items.append(item)
        total += item.line_total

    return items, total


# =========================================================
#  VIEWS
# =========================================================
def cart_view(request):
    """
    URL:
      path("cart/", cart_view, name="cart")
    """
    cart_items, cart_total = _build_cart_items(request)
    _sync_cart_badge_count(request)  # ✅ au cas où
    return render(
        request,
        "economic/ecommerce/cart.html",
        {"cart_items": cart_items, "cart_total": cart_total},
    )


@require_POST
def add_to_cart_view(request, product_id):
    """
    URL:
      path("cart/items/add/<int:product_id>/", add_to_cart_view, name="add_to_cart")
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    raw = _get_cart_raw(request)

    quantity = request.POST.get("quantity") or "1"
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1
    quantity = max(quantity, 1)

    raw[str(product.id)] = int(raw.get(str(product.id), 0)) + quantity
    _save_cart_raw(request, raw)  # ✅ sync badge inside

    # product.name (Parler) OK si langue active, sinon fallback
    prod_name = getattr(product, "name", None) or str(product)

    messages.success(
        request,
        _("%(product)s a été ajouté au panier.") % {"product": prod_name},
    )
    return redirect(request.POST.get("next") or reverse("economic:ecommerce:cart"))


@require_POST
def update_cart_view(request, item_id):
    """
    URL:
      path("cart/update/<int:item_id>/", update_cart_view, name="update_cart")

    item_id = product_id (panier session)
    """
    raw = _get_cart_raw(request)
    pid_str = str(item_id)

    if pid_str not in raw:
        return redirect(reverse("economic:ecommerce:cart"))

    quantity = request.POST.get("quantity") or "1"
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    if quantity <= 0:
        raw.pop(pid_str, None)
    else:
        raw[pid_str] = max(quantity, 1)

    _save_cart_raw(request, raw)  # ✅ sync badge inside
    messages.success(request, _("Votre panier a été mis à jour."))
    return redirect(request.POST.get("next") or reverse("economic:ecommerce:cart"))


@require_POST
def remove_from_cart_view(request, item_id):
    """
    URL:
      path("cart/items/remove/<int:item_id>/", remove_from_cart_view, name="remove_from_cart")

    item_id = product_id (panier session)
    """
    raw = _get_cart_raw(request)
    pid_str = str(item_id)

    if pid_str in raw:
        raw.pop(pid_str, None)
        _save_cart_raw(request, raw)  # ✅ sync badge inside
        messages.success(request, _("Produit retiré du panier."))

    return redirect(request.POST.get("next") or reverse("economic:ecommerce:cart"))







# # economic/ecommerce/views/cart.py
# from dataclasses import dataclass
# from decimal import Decimal

# from django.contrib import messages
# from django.shortcuts import get_object_or_404, redirect, render
# from django.urls import reverse
# from django.utils.translation import gettext as _
# from django.views.decorators.http import require_POST

# from ..models.product import Product

# CART_SESSION_KEY = "ecommerce_cart"

# def _sync_cart_badge_count(request):
#     """
#     Met à jour request.session['cart_items_count'] après chaque action panier.
#     DB si possible, sinon session.
#     """
#     from economic.ecommerce.context_processors import _count_cart_items_db, _count_cart_items_session

#     count = _count_cart_items_db(request)
#     if not count:
#         count = _count_cart_items_session(request)

#     try:
#         request.session["cart_items_count"] = int(count)
#         request.session.modified = True
#     except Exception:
#         pass

# @dataclass
# class CartItem:
#     product: Product
#     quantity: int
#     unit_price: Decimal

#     @property
#     def line_total(self) -> Decimal:
#         return self.unit_price * self.quantity


# def _get_cart_raw(request) -> dict:
#     return request.session.get(CART_SESSION_KEY, {})


# def _save_cart_raw(request, data: dict) -> None:
#     request.session[CART_SESSION_KEY] = data
#     request.session.modified = True


# def _build_cart_items(request):
#     raw = _get_cart_raw(request)

#     product_ids = []
#     for pid in raw.keys():
#         try:
#             product_ids.append(int(pid))
#         except ValueError:
#             continue

#     products = Product.objects.filter(id__in=product_ids, is_active=True)
#     products_by_id = {p.id: p for p in products}

#     items: list[CartItem] = []
#     total = Decimal("0.00")

#     for pid_str, qty in raw.items():
#         try:
#             pid = int(pid_str)
#         except ValueError:
#             continue

#         product = products_by_id.get(pid)
#         if not product:
#             continue

#         try:
#             quantity = int(qty)
#         except (TypeError, ValueError):
#             quantity = 1

#         if quantity < 1:
#             quantity = 1

#         unit_price = getattr(product, "price", Decimal("0.00")) or Decimal("0.00")
#         item = CartItem(product=product, quantity=quantity, unit_price=unit_price)
#         items.append(item)
#         total += item.line_total

#     return items, total


# def cart_view(request):
#     """
#     URL:
#       path("cart/", cart_view, name="cart")
#     """
#     cart_items, cart_total = _build_cart_items(request)
#     return render(
#         request,
#         "economic/ecommerce/cart.html",
#         {"cart_items": cart_items, "cart_total": cart_total},
#     )


# @require_POST
# def add_to_cart_view(request, product_id):
#     """
#     URL:
#       path("cart/items/add/<int:product_id>/", add_to_cart_view, name="add_to_cart")
#     """
#     product = get_object_or_404(Product, pk=product_id, is_active=True)
#     raw = _get_cart_raw(request)

#     quantity = request.POST.get("quantity") or "1"
#     try:
#         quantity = int(quantity)
#     except ValueError:
#         quantity = 1
#     quantity = max(quantity, 1)

#     raw[str(product.id)] = int(raw.get(str(product.id), 0)) + quantity
#     _save_cart_raw(request, raw)

#     messages.success(request, _("%(product)s a été ajouté au panier.") % {"product": product.name})
#     return redirect(request.POST.get("next") or reverse("economic:ecommerce:cart"))


# @require_POST
# def update_cart_view(request, item_id):
#     """
#     URL:
#       path("cart/update/<int:item_id>/", update_cart_view, name="update_cart")

#     item_id = product_id (panier session)
#     """
#     raw = _get_cart_raw(request)
#     pid_str = str(item_id)

#     if pid_str not in raw:
#         return redirect(reverse("economic:ecommerce:cart"))

#     quantity = request.POST.get("quantity") or "1"
#     try:
#         quantity = int(quantity)
#     except ValueError:
#         quantity = 1

#     if quantity <= 0:
#         raw.pop(pid_str, None)
#     else:
#         raw[pid_str] = quantity

#     _save_cart_raw(request, raw)
#     messages.success(request, _("Votre panier a été mis à jour."))
#     return redirect(reverse("economic:ecommerce:cart"))


# @require_POST
# def remove_from_cart_view(request, item_id):
#     """
#     URL:
#       path("cart/items/remove/<int:item_id>/", remove_from_cart_view, name="remove_from_cart")

#     item_id = product_id (panier session)
#     """
#     raw = _get_cart_raw(request)
#     pid_str = str(item_id)
#     if pid_str in raw:
#         raw.pop(pid_str)
#         _save_cart_raw(request, raw)
#         messages.success(request, _("Produit retiré du panier."))

#     return redirect(request.POST.get("next") or reverse("economic:ecommerce:cart"))





# # economic/ecommerce/views/cart.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required

# from ..models.cart import Cart
# from ..models.cart_item import CartItem
# from ..models.product import Product


# @login_required
# def cart_view(request):
#     cart, _ = Cart.objects.get_or_create(user=request.user)
#     items = cart.items.select_related("product")

#     context = {
#         "cart_items": items,
#         "cart_total": cart.total_amount,
#     }
#     return render(request, "economic/ecommerce/cart.html", context)


# @login_required
# def add_to_cart_view(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, _ = Cart.objects.get_or_create(user=request.user)

#     item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         product=product,
#         defaults={"unit_price": product.price},
#     )

#     if not created:
#         item.quantity += 1

#     item.save()
#     return redirect("economic:ecommerce:cart")


# @login_required
# def update_cart_view(request, item_id):
#     item = get_object_or_404(
#         CartItem,
#         id=item_id,
#         cart__user=request.user,
#     )

#     if request.method == "POST":
#         qty = int(request.POST.get("quantity", 1))
#         if qty > 0:
#             item.quantity = qty
#             item.save()
#         else:
#             item.delete()

#     return redirect("economic:ecommerce:cart")


# @login_required
# def remove_from_cart_view(request, item_id):
#     item = get_object_or_404(
#         CartItem,
#         id=item_id,
#         cart__user=request.user,
#     )
#     item.delete()
#     return redirect("economic:ecommerce:cart")







# # economic/ecommerce/views/cart.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# # from django.urls import reverse

# from ..services.cart_service import (
#     get_or_create_cart,
#     add_product_to_cart,
#     remove_cart_item,
# )


# # def some_view(request):
# #     return render(request, "template.html", {
# #         "eco_store_url": reverse("economic:ecommerce:store"),
# #     })

# @login_required
# def cart_view(request):
#     cart = get_or_create_cart(request.user)
#     return render(request, "economic/ecommerce/cart.html", {"cart": cart})


# @login_required
# def add_to_cart_view(request, product_id):
#     add_product_to_cart(request.user, product_id)
#     return redirect("ecommerce:cart")


# @login_required
# def remove_from_cart_view(request, item_id):
#     remove_cart_item(item_id, request.user)
#     return redirect("ecommerce:cart")
