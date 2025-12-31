# economic/ecommerce/views/wishlist.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..models.wishlist import Wishlist
from ..models.wishlist_item import WishlistItem
from ..models.product import Product


@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, "ecommerce/wishlist.html", {"wishlist": wishlist})


@login_required
def add_to_wishlist_view(request, product_id):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
    )
    return redirect("ecommerce:wishlist")


@login_required
def remove_from_wishlist_view(request, product_id):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    WishlistItem.objects.filter(
        wishlist=wishlist,
        product_id=product_id,
    ).delete()
    return redirect("ecommerce:wishlist")
