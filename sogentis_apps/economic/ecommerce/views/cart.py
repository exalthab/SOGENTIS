# economic/ecommerce/views/cart.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models.cart import Cart
from ..models.cart_item import CartItem
from ..models.product import Product


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product")

    context = {
        "cart_items": items,
        "cart_total": cart.total_amount,
    }
    return render(request, "economic/ecommerce/cart.html", context)


@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"unit_price": product.price},
    )

    if not created:
        item.quantity += 1

    item.save()
    return redirect("economic:ecommerce:cart")


@login_required
def update_cart_view(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    if request.method == "POST":
        qty = int(request.POST.get("quantity", 1))
        if qty > 0:
            item.quantity = qty
            item.save()
        else:
            item.delete()

    return redirect("economic:ecommerce:cart")


@login_required
def remove_from_cart_view(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )
    item.delete()
    return redirect("economic:ecommerce:cart")







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
