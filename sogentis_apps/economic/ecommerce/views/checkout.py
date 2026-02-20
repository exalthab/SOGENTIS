# economic/ecommerce/views/checkout.py
from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.product import Product
from .cart import _build_cart_items, _save_cart_raw, _normalize_cart_against_stock


def _get_post_value(request, key: str, default: str = "") -> str:
    val = request.POST.get(key, default)
    if val is None:
        return default
    return str(val).strip()


def _to_int(value, default=1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_stock(product: Product) -> int:
    try:
        stock = int(getattr(product, "stock", 0) or 0)
    except Exception:
        stock = 0
    return max(stock, 0)


def _recalc_total(cart_items) -> Decimal:
    total = Decimal("0.00")
    for it in cart_items:
        try:
            total += Decimal(str(it.line_total))
        except Exception:
            continue
    return total


def _try_apply_buy_now(request) -> bool:
    buy_now = (request.GET.get("buy_now") or "").strip()
    if buy_now != "1":
        return False

    pid_raw = (request.GET.get("product_id") or "").strip()
    qty_raw = (request.GET.get("qty") or "1").strip()

    pid = _to_int(pid_raw, 0)
    qty = _to_int(qty_raw, 1)
    qty = max(1, min(qty, 1_000_000))

    if pid <= 0:
        return False

    product = Product.objects.filter(pk=pid, is_active=True).first()
    if not product:
        messages.error(request, _("Produit introuvable ou indisponible."))
        return False

    stock = _get_stock(product)
    if stock <= 0:
        messages.error(request, _("Produit en rupture de stock."))
        return False

    qty = min(qty, stock)
    _save_cart_raw(request, {str(pid): int(qty)})
    return True


def checkout_view(request):
    # BuyNow -> panier minimal
    if request.method == "GET" and _try_apply_buy_now(request):
        return redirect("economic:ecommerce:checkout")

    _normalize_cart_against_stock(request)
    cart_items, cart_total = _build_cart_items(request)
    cart_total = _recalc_total(cart_items)

    if not cart_items:
        messages.warning(request, _("Votre panier est vide."))
        return redirect("economic:ecommerce:cart")

    # Prefill
    initial = {
        "billing_name": "",
        "email": "",
        "billing_phone": "",
        "billing_address": "",
        "billing_zip": "",
        "billing_city": "",
        "billing_country": "",
        "customer_note": "",
    }
    if request.user.is_authenticated:
        full_name = (
            getattr(request.user, "get_full_name", lambda: "")()
            or getattr(request.user, "username", "")
            or ""
        )
        initial["billing_name"] = full_name
        initial["email"] = getattr(request.user, "email", "") or ""

    if request.method == "POST":
        _normalize_cart_against_stock(request)
        cart_items, cart_total = _build_cart_items(request)
        cart_total = _recalc_total(cart_items)

        if not cart_items:
            messages.error(request, _("Des articles ne sont plus disponibles. Votre panier a été mis à jour."))
            return redirect("economic:ecommerce:cart")

        billing_name = _get_post_value(request, "billing_name", initial["billing_name"])
        email = _get_post_value(request, "email", initial["email"])
        billing_phone = _get_post_value(request, "billing_phone", "")
        billing_address = _get_post_value(request, "billing_address", "")
        billing_zip = _get_post_value(request, "billing_zip", "")
        billing_city = _get_post_value(request, "billing_city", "")
        billing_country = _get_post_value(request, "billing_country", "")
        customer_note = _get_post_value(request, "customer_note", "")

        errors: list[str] = []
        if not billing_name:
            errors.append(_("Nom / Prénom requis."))
        if not email or "@" not in email:
            errors.append(_("Email valide requis."))
        if not billing_address:
            errors.append(_("Adresse requise."))
        if not billing_city:
            errors.append(_("Ville requise."))
        if not billing_country:
            errors.append(_("Pays requis."))

        if errors:
            for e in errors:
                messages.error(request, e)

            initial.update({
                "billing_name": billing_name,
                "email": email,
                "billing_phone": billing_phone,
                "billing_address": billing_address,
                "billing_zip": billing_zip,
                "billing_city": billing_city,
                "billing_country": billing_country,
                "customer_note": customer_note,
            })
        else:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,  # ton modèle Order.user n'est pas nullable
                    customer_email=email,
                    billing_name=billing_name,
                    billing_phone=billing_phone,
                    billing_address=billing_address,
                    billing_zip=billing_zip,
                    billing_city=billing_city,
                    billing_country=billing_country,
                    customer_note=customer_note,
                    status=Order.STATUS_PENDING,
                    total_amount=cart_total,  # Order.save() recalc ensuite aussi
                )

                for item in cart_items:
                    p = item.product
                    try:
                        pname = p.safe_translation_getter("name", any_language=True) or ""
                    except Exception:
                        pname = ""
                    if not pname:
                        pname = getattr(p, "name", None) or str(p)

                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        product_name=pname,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        currency=getattr(order, "currency", "XOF") or "XOF",
                    )

                try:
                    order.recalc_totals(save=True)
                except Exception:
                    pass

            _save_cart_raw(request, {})
            messages.success(request, _("Commande créée. Choisissez un moyen de paiement."))
            return redirect("economic:ecommerce:choose_payment", uuid=order.uuid)

    return render(
        request,
        "economic/ecommerce/checkout.html",
        {"cart_items": cart_items, "cart_total": cart_total, "initial": initial},
    )







# # economic/ecommerce/views/checkout.py
# from __future__ import annotations

# from decimal import Decimal

# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order
# from ..models.order_item import OrderItem
# from ..models.product import Product
# from .cart import _build_cart_items, _save_cart_raw, _normalize_cart_against_stock


# def _get_post_value(request, key: str, default: str = "") -> str:
#     val = request.POST.get(key, default)
#     if val is None:
#         return default
#     return str(val).strip()


# def _to_int(value, default=1) -> int:
#     try:
#         return int(value)
#     except (TypeError, ValueError):
#         return default


# def _get_stock(product: Product) -> int:
#     try:
#         stock = int(getattr(product, "stock", 0) or 0)
#     except Exception:
#         stock = 0
#     return max(stock, 0)


# def _recalc_total(cart_items) -> Decimal:
#     total = Decimal("0.00")
#     for it in cart_items:
#         try:
#             total += Decimal(str(it.line_total))
#         except Exception:
#             continue
#     return total


# def _try_apply_buy_now(request) -> bool:
#     """
#     BUY NOW:
#     /checkout/?buy_now=1&product_id=..&qty=..
#     - vérifie produit actif
#     - refuse si stock=0
#     - clamp qty au stock
#     - injecte un panier session minimal
#     """
#     buy_now = (request.GET.get("buy_now") or "").strip()
#     if buy_now != "1":
#         return False

#     pid_raw = (request.GET.get("product_id") or "").strip()
#     qty_raw = (request.GET.get("qty") or "1").strip()

#     pid = _to_int(pid_raw, 0)
#     qty = _to_int(qty_raw, 1)
#     qty = max(1, min(qty, 1_000_000))

#     if pid <= 0:
#         return False

#     product = Product.objects.filter(pk=pid, is_active=True).first()
#     if not product:
#         messages.error(request, _("Produit introuvable ou indisponible."))
#         return False

#     stock = _get_stock(product)
#     if stock <= 0:
#         messages.error(request, _("Produit en rupture de stock."))
#         return False

#     qty = min(qty, stock)

#     try:
#         _save_cart_raw(request, {str(pid): int(qty)})
#         return True
#     except Exception:
#         return False


# def checkout_view(request):
#     """
#     Checkout sans Django Form.
#     Template : economic/ecommerce/checkout.html

#     IMPORTANT (compat modèle Order):
#     - Order n'a PAS billing_name/billing_address/...
#     - On collecte seulement:
#         - billing_name (utilisé côté UI, pas stocké dans Order tant que le champ n'existe pas)
#         - email -> stocké dans Order.customer_email
#     """
#     # BUY NOW -> panier minimal puis redirige (évite resoumission)
#     if request.method == "GET" and _try_apply_buy_now(request):
#         return redirect("economic:ecommerce:checkout")

#     # Normaliser panier contre stock (enlève ruptures + clamp)
#     _normalize_cart_against_stock(request)

#     cart_items, cart_total = _build_cart_items(request)
#     cart_total = _recalc_total(cart_items)

#     if not cart_items:
#         messages.warning(request, _("Votre panier est vide."))
#         return redirect("economic:ecommerce:cart")

#     # Pré-remplissage
#     initial = {
#         "billing_name": "",
#         "email": "",
#     }
#     if request.user.is_authenticated:
#         full_name = (
#             getattr(request.user, "get_full_name", lambda: "")()
#             or getattr(request.user, "username", "")
#             or ""
#         )
#         initial["billing_name"] = full_name
#         initial["email"] = getattr(request.user, "email", "") or ""

#     if request.method == "POST":
#         # re-normaliser au POST (stock peut changer)
#         _normalize_cart_against_stock(request)
#         cart_items, cart_total = _build_cart_items(request)
#         cart_total = _recalc_total(cart_items)

#         if not cart_items:
#             messages.error(
#                 request,
#                 _("Un ou plusieurs articles ne sont plus disponibles. Votre panier a été mis à jour."),
#             )
#             return redirect("economic:ecommerce:cart")

#         billing_name = _get_post_value(request, "billing_name", initial["billing_name"])
#         email = _get_post_value(request, "email", initial["email"])

#         errors: list[str] = []
#         if not billing_name:
#             errors.append(_("Nom / Prénom requis."))
#         if not email or "@" not in email:
#             errors.append(_("Email valide requis."))

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             initial.update({"billing_name": billing_name, "email": email})
#         else:
#             # Si ton Order.user est NON NULLABLE -> il faut forcer login.
#             # Ici je fais le comportement "prod-safe":
#             must_be_logged_in = False
#             try:
#                 user_field = Order._meta.get_field("user")
#                 must_be_logged_in = bool(getattr(user_field, "null", False) is False)
#             except Exception:
#                 must_be_logged_in = True

#             if must_be_logged_in and not request.user.is_authenticated:
#                 messages.error(request, _("Veuillez vous connecter pour finaliser la commande."))
#                 return redirect("accounts_users:login")

#             with transaction.atomic():
#                 order = Order.objects.create(
#                     user=request.user if request.user.is_authenticated else None,
#                     total_amount=cart_total,
#                     customer_email=email,
#                     status=Order.STATUS_PENDING,
#                 )

#                 for item in cart_items:
#                     p = item.product

#                     # Snapshot name (Parler safe)
#                     pname = ""
#                     try:
#                         pname = p.safe_translation_getter("name", any_language=True) or ""
#                     except Exception:
#                         pname = ""
#                     if not pname:
#                         pname = getattr(p, "name", None) or str(p)

#                     OrderItem.objects.create(
#                         order=order,
#                         product=p,
#                         product_name=pname,
#                         unit_price=item.unit_price,
#                         quantity=item.quantity,
#                         currency=getattr(order, "currency", "XOF") or "XOF",
#                     )

#                 # ton Order.save() recalc totals via items -> OK
#                 try:
#                     order.recalc_totals(save=True)
#                 except Exception:
#                     pass

#             _save_cart_raw(request, {})  # vider panier
#             messages.success(request, _("Commande créée. Choisissez un moyen de paiement."))
#             return redirect("economic:ecommerce:choose_payment", uuid=order.uuid)

#     context = {
#         "cart_items": cart_items,
#         "cart_total": cart_total,
#         "initial": initial,
#     }
#     return render(request, "economic/ecommerce/checkout.html", context)






# # economic/ecommerce/views/checkout.py
# from __future__ import annotations

# from decimal import Decimal

# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order
# from ..models.order_item import OrderItem
# from ..models.product import Product
# from .cart import _build_cart_items, _save_cart_raw, _normalize_cart_against_stock


# def _get_post_value(request, key: str, default: str = "") -> str:
#     val = request.POST.get(key, default)
#     if val is None:
#         return default
#     return str(val).strip()


# def _to_int(value, default=1) -> int:
#     try:
#         return int(value)
#     except (TypeError, ValueError):
#         return default


# def _get_stock(product: Product) -> int:
#     try:
#         stock = int(getattr(product, "stock", 0) or 0)
#     except Exception:
#         stock = 0
#     return max(stock, 0)


# def _try_apply_buy_now(request) -> bool:
#     """
#     Si la page checkout est appelée avec ?buy_now=1&product_id=..&qty=..
#     on injecte un panier session minimal puis on redirige sur checkout (sans query).

#     ✅ Corrigé:
#     - vérifie produit actif
#     - clamp qty au stock
#     - refuse si stock=0
#     """
#     buy_now = (request.GET.get("buy_now") or "").strip()
#     if buy_now != "1":
#         return False

#     pid_raw = (request.GET.get("product_id") or "").strip()
#     qty_raw = (request.GET.get("qty") or "1").strip()

#     pid = _to_int(pid_raw, 0)
#     qty = _to_int(qty_raw, 1)
#     qty = max(1, min(qty, 1_000_000))

#     if pid <= 0:
#         return False

#     product = Product.objects.filter(pk=pid, is_active=True).first()
#     if not product:
#         messages.error(request, _("Produit introuvable ou indisponible."))
#         return False

#     stock = _get_stock(product)
#     if stock <= 0:
#         messages.error(request, _("Produit en rupture de stock."))
#         return False

#     qty = min(qty, stock)

#     try:
#         cart_raw = {str(pid): int(qty)}
#         _save_cart_raw(request, cart_raw)
#         return True
#     except Exception:
#         return False


# def _recalc_total(cart_items) -> Decimal:
#     total = Decimal("0.00")
#     for it in cart_items:
#         try:
#             total += it.line_total
#         except Exception:
#             continue
#     return total


# def checkout_view(request):
#     """
#     Checkout sans formulaire Django (pas de CheckoutForm).
#     - Support BUY NOW via query (?buy_now=1&product_id=..&qty=..)
#     - Affiche la page checkout (GET)
#     - Crée la commande (POST)
#     Template : economic/ecommerce/checkout.html
#     URL : path("checkout/", checkout_view, name="checkout")

#     ✅ Stock-safe:
#     - normalise le panier contre stock avant affichage
#     - re-normalise au POST avant création commande
#     """
#     # ✅ BuyNow -> on force un panier minimal puis on redirige (évite resoumission)
#     if request.method == "GET" and _try_apply_buy_now(request):
#         return redirect("economic:ecommerce:checkout")

#     # ✅ Normaliser panier contre stock (enlève ruptures + clamp)
#     _normalize_cart_against_stock(request)

#     cart_items, cart_total = _build_cart_items(request)
#     cart_total = _recalc_total(cart_items)

#     if not cart_items:
#         messages.warning(request, _("Votre panier est vide."))
#         return redirect("economic:ecommerce:cart")

#     # Pré-remplissage simple si connecté
#     initial = {
#         "billing_name": "",
#         "email": "",
#         "billing_address": "",
#         "billing_zip": "",
#         "billing_city": "",
#         "billing_country": "",
#     }
#     if request.user.is_authenticated:
#         full_name = getattr(request.user, "get_full_name", lambda: "")() or getattr(request.user, "username", "")
#         initial["billing_name"] = full_name
#         initial["email"] = getattr(request.user, "email", "") or ""

#     if request.method == "POST":
#         # ✅ Re-normaliser au moment de payer (stock peut changer)
#         _normalize_cart_against_stock(request)
#         cart_items, cart_total = _build_cart_items(request)
#         cart_total = _recalc_total(cart_items)

#         if not cart_items:
#             messages.error(request, _("Un ou plusieurs articles ne sont plus disponibles. Votre panier a été mis à jour."))
#             return redirect("economic:ecommerce:cart")

#         billing_name = _get_post_value(request, "billing_name", initial["billing_name"])
#         email = _get_post_value(request, "email", initial["email"])
#         billing_address = _get_post_value(request, "billing_address", "")
#         billing_zip = _get_post_value(request, "billing_zip", "")
#         billing_city = _get_post_value(request, "billing_city", "")
#         billing_country = _get_post_value(request, "billing_country", "")

#         # Validation minimale
#         errors: list[str] = []
#         if not billing_name:
#             errors.append(_("Nom / Prénom requis."))
#         if not email or "@" not in email:
#             errors.append(_("Email valide requis."))

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             initial.update(
#                 {
#                     "billing_name": billing_name,
#                     "email": email,
#                     "billing_address": billing_address,
#                     "billing_zip": billing_zip,
#                     "billing_city": billing_city,
#                     "billing_country": billing_country,
#                 }
#             )
#         else:
#             # ✅ Transaction = commande + items atomiques
#             with transaction.atomic():
#                 order = Order.objects.create(
#                     user=request.user if request.user.is_authenticated else None,
#                     total_amount=cart_total,
#                     billing_name=billing_name,
#                     billing_address=billing_address,
#                     billing_zip=billing_zip,
#                     billing_city=billing_city,
#                     billing_country=billing_country,
#                     customer_email=email,
#                     # status="PENDING",
#                     status=Order.STATUS_PENDING,

#                 )

#                 for item in cart_items:
#                     # Snapshot safe
#                     p = item.product
#                     pname = getattr(p, "name", None) or str(p)

#                     OrderItem.objects.create(
#                         order=order,
#                         product=p,
#                         product_name=pname,
#                         unit_price=item.unit_price,
#                         quantity=item.quantity,
#                         # line_total=item.line_total,
#                         currency=getattr(order, "currency", "XOF") or "XOF",

#                     )

#             # ✅ Vider panier session
#             _save_cart_raw(request, {})

#             messages.success(request, _("Commande créée. Choisissez un moyen de paiement."))
#             return redirect("economic:ecommerce:choose_payment", uuid=order.uuid)

#     context = {
#         "cart_items": cart_items,
#         "cart_total": cart_total,
#         "initial": initial,
#     }
#     return render(request, "economic/ecommerce/checkout.html", context)





# # economic/ecommerce/views/checkout.py
# from __future__ import annotations

# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order
# from ..models.order_item import OrderItem
# from .cart import _build_cart_items, _save_cart_raw


# def _get_post_value(request, key: str, default: str = "") -> str:
#     val = request.POST.get(key, default)
#     if val is None:
#         return default
#     return str(val).strip()


# def _try_apply_buy_now(request) -> bool:
#     """
#     Si la page checkout est appelée avec ?buy_now=1&product_id=..&qty=..
#     on injecte un panier session minimal puis on redirige sur checkout (sans query).
#     """
#     buy_now = (request.GET.get("buy_now") or "").strip()
#     if buy_now != "1":
#         return False

#     pid = (request.GET.get("product_id") or "").strip()
#     qty_raw = (request.GET.get("qty") or "1").strip()

#     try:
#         qty = int(qty_raw)
#     except Exception:
#         qty = 1

#     qty = max(1, min(qty, 1_000_000))
#     if not pid:
#         return False

#     # Format panier: on reste compatible avec ton cart.py (dict en session)
#     # Ici, on met {product_id: quantity}
#     try:
#         cart_raw = {str(pid): int(qty)}
#         _save_cart_raw(request, cart_raw)
#         return True
#     except Exception:
#         return False


# def checkout_view(request):
#     """
#     Checkout sans formulaire Django (pas de CheckoutForm).
#     - Support BUY NOW via query (?buy_now=1&product_id=..&qty=..)
#     - Affiche la page checkout (GET)
#     - Crée la commande (POST)
#     Template : economic/ecommerce/checkout.html
#     URL : path("checkout/", checkout_view, name="checkout")
#     """
#     # ✅ BuyNow -> on force un panier minimal puis on redirige (évite resoumission)
#     if request.method == "GET" and _try_apply_buy_now(request):
#         return redirect("economic:ecommerce:checkout")

#     cart_items, cart_total = _build_cart_items(request)
#     if not cart_items:
#         messages.warning(request, _("Votre panier est vide."))
#         return redirect("economic:ecommerce:cart")

#     # Pré-remplissage simple si connecté
#     initial = {
#         "billing_name": "",
#         "email": "",
#         "billing_address": "",
#         "billing_zip": "",
#         "billing_city": "",
#         "billing_country": "",
#     }
#     if request.user.is_authenticated:
#         full_name = getattr(request.user, "get_full_name", lambda: "")() or getattr(request.user, "username", "")
#         initial["billing_name"] = full_name
#         initial["email"] = getattr(request.user, "email", "") or ""

#     if request.method == "POST":
#         billing_name = _get_post_value(request, "billing_name", initial["billing_name"])
#         email = _get_post_value(request, "email", initial["email"])
#         billing_address = _get_post_value(request, "billing_address", "")
#         billing_zip = _get_post_value(request, "billing_zip", "")
#         billing_city = _get_post_value(request, "billing_city", "")
#         billing_country = _get_post_value(request, "billing_country", "")

#         # Validation minimale
#         errors = []
#         if not billing_name:
#             errors.append(_("Nom / Prénom requis."))
#         if not email or "@" not in email:
#             errors.append(_("Email valide requis."))

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             initial.update(
#                 {
#                     "billing_name": billing_name,
#                     "email": email,
#                     "billing_address": billing_address,
#                     "billing_zip": billing_zip,
#                     "billing_city": billing_city,
#                     "billing_country": billing_country,
#                 }
#             )
#         else:
#             order = Order.objects.create(
#                 user=request.user if request.user.is_authenticated else None,
#                 total_amount=cart_total,
#                 billing_name=billing_name,
#                 billing_address=billing_address,
#                 billing_zip=billing_zip,
#                 billing_city=billing_city,
#                 billing_country=billing_country,
#                 email=email,
#                 status="PENDING",
#             )

#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     product_name=item.product.name,
#                     unit_price=item.unit_price,
#                     quantity=item.quantity,
#                     line_total=item.line_total,
#                 )

#             _save_cart_raw(request, {})
#             messages.success(request, _("Commande créée. Choisissez un moyen de paiement."))
#             return redirect("economic:ecommerce:choose_payment", uuid=order.uuid)

#     context = {
#         "cart_items": cart_items,
#         "cart_total": cart_total,
#         "initial": initial,
#     }
#     return render(request, "economic/ecommerce/checkout.html", context)






# # economic/ecommerce/views/checkout.py

# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order
# from ..models.order_item import OrderItem
# from .cart import _build_cart_items, _save_cart_raw


# def _get_post_value(request, key: str, default: str = "") -> str:
#     val = request.POST.get(key, default)
#     if val is None:
#         return default
#     return str(val).strip()


# def checkout_view(request):
#     """
#     Checkout sans formulaire Django (pas de CheckoutForm).
#     - Affiche la page checkout (GET)
#     - Crée la commande (POST)
#     Template : economic/ecommerce/checkout.html
#     URL : path("checkout/", checkout_view, name="checkout")
#     """
#     cart_items, cart_total = _build_cart_items(request)
#     if not cart_items:
#         messages.warning(request, _("Votre panier est vide."))
#         return redirect("economic:ecommerce:cart")

#     # Pré-remplissage simple si connecté
#     initial = {
#         "billing_name": "",
#         "email": "",
#         "billing_address": "",
#         "billing_zip": "",
#         "billing_city": "",
#         "billing_country": "",
#     }
#     if request.user.is_authenticated:
#         full_name = getattr(request.user, "get_full_name", lambda: "")() or request.user.username
#         initial["billing_name"] = full_name
#         initial["email"] = getattr(request.user, "email", "") or ""

#     if request.method == "POST":
#         billing_name = _get_post_value(request, "billing_name", initial["billing_name"])
#         email = _get_post_value(request, "email", initial["email"])
#         billing_address = _get_post_value(request, "billing_address", "")
#         billing_zip = _get_post_value(request, "billing_zip", "")
#         billing_city = _get_post_value(request, "billing_city", "")
#         billing_country = _get_post_value(request, "billing_country", "")

#         # Validation minimale
#         errors = []
#         if not billing_name:
#             errors.append(_("Nom / Prénom requis."))
#         if not email or "@" not in email:
#             errors.append(_("Email valide requis."))

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             # On ré-affiche le checkout avec les valeurs saisies
#             initial.update({
#                 "billing_name": billing_name,
#                 "email": email,
#                 "billing_address": billing_address,
#                 "billing_zip": billing_zip,
#                 "billing_city": billing_city,
#                 "billing_country": billing_country,
#             })
#         else:
#             # Création commande
#             order = Order.objects.create(
#                 user=request.user if request.user.is_authenticated else None,
#                 total_amount=cart_total,
#                 billing_name=billing_name,
#                 billing_address=billing_address,
#                 billing_zip=billing_zip,
#                 billing_city=billing_city,
#                 billing_country=billing_country,
#                 email=email,
#                 status="PENDING",
#             )

#             # Items
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     product_name=item.product.name,
#                     unit_price=item.unit_price,
#                     quantity=item.quantity,
#                     line_total=item.line_total,
#                 )

#             # Vider panier session
#             _save_cart_raw(request, {})

#             messages.success(request, _("Commande créée. Choisissez un moyen de paiement."))
#             return redirect("economic:ecommerce:choose_payment", uuid=order.uuid)

#     context = {
#         "cart_items": cart_items,
#         "cart_total": cart_total,
#         "initial": initial,  # à utiliser dans checkout.html pour pré-remplir les champs
#     }
#     return render(request, "economic/ecommerce/checkout.html", context)





# # economic/ecommerce/views/checkout.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db import transaction

# from ..models.cart import Cart
# from ..models.order import Order
# from ..models.order_item import OrderItem


# @login_required
# def checkout_view(request):
#     """
#     Étape 1 du checkout :
#     - valider le panier
#     - créer la commande
#     - créer les lignes de commande
#     - vider le panier
#     - rediriger vers le choix du paiement
#     """

#     # 🔹 Récupération du panier utilisateur
#     cart = (
#         Cart.objects.filter(user=request.user)
#         .prefetch_related("items__product")
#         .first()
#     )

#     # 🔹 Panier vide → redirection
#     if not cart or not cart.items.exists():
#         return redirect("economic:ecommerce:cart")

#     cart_items = cart.items.all()
#     total_amount = cart.total_amount

#     if request.method == "POST":
#         with transaction.atomic():

#             # 1️⃣ Création de la commande
#             order = Order.objects.create(
#                 user=request.user,
#                 total_amount=total_amount,
#                 status=Order.STATUS_PENDING,
#             )

#             # 2️⃣ Création des lignes de commande
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     unit_price=item.unit_price,
#                 )

#             # 3️⃣ Vider le panier (commande créée = source de vérité)
#             cart.items.all().delete()

#         # 4️⃣ Redirection vers le CHOIX DU PAIEMENT
#         return redirect(
#             "economic:ecommerce:choose_payment",
#             uuid=order.uuid,
#         )

#     # 🔹 Affichage page checkout (récapitulatif uniquement)
#     context = {
#         "cart": cart,
#         "cart_items": cart_items,
#         "total_amount": total_amount,
#     }

#     return render(
#         request,
#         "economic/ecommerce/checkout.html",
#         context,
#     )







# # /economic/ecommerce/views/checkout.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db import transaction

# from ..models.cart import Cart
# from ..models.order import Order
# from ..models.order_item import OrderItem

# from ..services.payment_service import initiate_payment


# @login_required
# def checkout_view(request):
#     # 🔹 Récupération du panier utilisateur
#     cart = Cart.objects.filter(user=request.user).prefetch_related(
#         "items__product"
#     ).first()

#     # 🔹 Panier vide → redirection
#     if not cart or not cart.items.exists():
#         return redirect("economic:ecommerce:cart")

#     cart_items = cart.items.all()
#     total_amount = cart.total_amount

#     if request.method == "POST":
#         payment_provider = request.POST.get("payment_method")

#         with transaction.atomic():
#             # 1️⃣ Création de la commande
#             order = Order.objects.create(
#                 user=request.user,
#                 total_amount=total_amount,
#                 status=Order.STATUS_PENDING,
#             )

#             # 2️⃣ Création des lignes de commande
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     unit_price=item.unit_price,
#                 )

#             # 3️⃣ Lancer le paiement
#             payment_url = initiate_payment(order, payment_provider)

#             # 4️⃣ Vider le panier
#             cart.items.all().delete()

#         # 🔹 Redirection vers le paiement ou succès
#         if payment_url:
#             return redirect(payment_url)

#         return redirect("economic:ecommerce:order_success", order.id)

#     # 🔹 Affichage page checkout
#     context = {
#         "cart": cart,
#         "cart_items": cart_items,
#         "total_amount": total_amount,
#         "payment_methods": [
#             ("stripe", "Carte bancaire (Stripe)"),
#             ("paypal", "PayPal"),
#             ("wave", "Wave"),
#             ("orange", "Orange Money"),
#         ],
#     }

#     return render(request, "economic/ecommerce/checkout.html", context)






# # economic/ecommerce/views/checkout.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from ..services.cart_service import get_or_create_cart
# from ..services.order_service import create_order_from_cart
# from ..services.payment_service import initiate_payment


# @login_required
# def checkout_view(request):
#     cart = get_or_create_cart(request.user)

#     if request.method == "POST":
#         provider = request.POST.get("payment_method")
#         order = create_order_from_cart(request.user, cart)

#         payment_url = initiate_payment(order, provider)
#         return redirect("economic:ecommerce:order_success", order.id)

#     return render(request, "economic/ecommerce/checkout.html", {
#         "cart": cart,
#         "payment_methods": [
#             ("stripe", "Carte bancaire (Stripe)"),
#             ("paypal", "PayPal"),
#             ("wave", "Wave"),
#             ("orange", "Orange Money"),
#         ]
#     })
