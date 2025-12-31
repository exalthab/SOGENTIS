# economic/ecommerce/views/checkout.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction

from ..models.cart import Cart
from ..models.order import Order
from ..models.order_item import OrderItem


@login_required
def checkout_view(request):
    """
    Étape 1 du checkout :
    - valider le panier
    - créer la commande
    - créer les lignes de commande
    - vider le panier
    - rediriger vers le choix du paiement
    """

    # 🔹 Récupération du panier utilisateur
    cart = (
        Cart.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .first()
    )

    # 🔹 Panier vide → redirection
    if not cart or not cart.items.exists():
        return redirect("economic:ecommerce:cart")

    cart_items = cart.items.all()
    total_amount = cart.total_amount

    if request.method == "POST":
        with transaction.atomic():

            # 1️⃣ Création de la commande
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                status=Order.STATUS_PENDING,
            )

            # 2️⃣ Création des lignes de commande
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

            # 3️⃣ Vider le panier (commande créée = source de vérité)
            cart.items.all().delete()

        # 4️⃣ Redirection vers le CHOIX DU PAIEMENT
        return redirect(
            "economic:ecommerce:choose_payment",
            uuid=order.uuid,
        )

    # 🔹 Affichage page checkout (récapitulatif uniquement)
    context = {
        "cart": cart,
        "cart_items": cart_items,
        "total_amount": total_amount,
    }

    return render(
        request,
        "economic/ecommerce/checkout.html",
        context,
    )







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
