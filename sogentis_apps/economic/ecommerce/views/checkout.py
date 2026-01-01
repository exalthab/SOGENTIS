# economic/ecommerce/views/checkout.py

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from ..models.order import Order
from ..models.order_item import OrderItem
from .cart import _build_cart_items, _save_cart_raw


def _get_post_value(request, key: str, default: str = "") -> str:
    val = request.POST.get(key, default)
    if val is None:
        return default
    return str(val).strip()


def checkout_view(request):
    """
    Checkout sans formulaire Django (pas de CheckoutForm).
    - Affiche la page checkout (GET)
    - Crée la commande (POST)
    Template : economic/ecommerce/checkout.html
    URL : path("checkout/", checkout_view, name="checkout")
    """
    cart_items, cart_total = _build_cart_items(request)
    if not cart_items:
        messages.warning(request, _("Votre panier est vide."))
        return redirect("economic:ecommerce:cart")

    # Pré-remplissage simple si connecté
    initial = {
        "billing_name": "",
        "email": "",
        "billing_address": "",
        "billing_zip": "",
        "billing_city": "",
        "billing_country": "",
    }
    if request.user.is_authenticated:
        full_name = getattr(request.user, "get_full_name", lambda: "")() or request.user.username
        initial["billing_name"] = full_name
        initial["email"] = getattr(request.user, "email", "") or ""

    if request.method == "POST":
        billing_name = _get_post_value(request, "billing_name", initial["billing_name"])
        email = _get_post_value(request, "email", initial["email"])
        billing_address = _get_post_value(request, "billing_address", "")
        billing_zip = _get_post_value(request, "billing_zip", "")
        billing_city = _get_post_value(request, "billing_city", "")
        billing_country = _get_post_value(request, "billing_country", "")

        # Validation minimale
        errors = []
        if not billing_name:
            errors.append(_("Nom / Prénom requis."))
        if not email or "@" not in email:
            errors.append(_("Email valide requis."))

        if errors:
            for e in errors:
                messages.error(request, e)
            # On ré-affiche le checkout avec les valeurs saisies
            initial.update({
                "billing_name": billing_name,
                "email": email,
                "billing_address": billing_address,
                "billing_zip": billing_zip,
                "billing_city": billing_city,
                "billing_country": billing_country,
            })
        else:
            # Création commande
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                total_amount=cart_total,
                billing_name=billing_name,
                billing_address=billing_address,
                billing_zip=billing_zip,
                billing_city=billing_city,
                billing_country=billing_country,
                email=email,
                status="PENDING",
            )

            # Items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    line_total=item.line_total,
                )

            # Vider panier session
            _save_cart_raw(request, {})

            messages.success(request, _("Commande créée. Choisissez un moyen de paiement."))
            return redirect("economic:ecommerce:choose_payment", uuid=order.uuid)

    context = {
        "cart_items": cart_items,
        "cart_total": cart_total,
        "initial": initial,  # à utiliser dans checkout.html pour pré-remplir les champs
    }
    return render(request, "economic/ecommerce/checkout.html", context)





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
