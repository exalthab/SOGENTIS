# economic/ecommerce/views/wishlist.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from ..models.product import Product
from ..models.wishlist import Wishlist
from ..models.wishlist_item import WishlistItem


@login_required
def wishlist_view(request):
    """
    URL:
      path("wishlist/", wishlist_view, name="wishlist")
    """
    wishlist, _created = Wishlist.objects.get_or_create(user=request.user)

    items = (
        WishlistItem.objects
        .filter(wishlist=wishlist)
        .select_related("product")
        .order_by("-added_at")
    )

    return render(
        request,
        "economic/ecommerce/wishlist.html",
        {
            "wishlist": wishlist,
            "wishlist_items": items,
        },
    )


@login_required
@require_POST
def add_to_wishlist_view(request, product_id):
    """
    URL:
      path("wishlist/items/add/<int:product_id>/", add_to_wishlist_view, name="wishlist_add")
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, _created = Wishlist.objects.get_or_create(user=request.user)

    obj, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
    )

    if created:
        messages.success(request, _("Produit ajouté à votre liste de souhaits."))
    else:
        messages.info(request, _("Ce produit est déjà dans votre liste de souhaits."))

    return redirect(
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("economic:ecommerce:wishlist")
    )


@login_required
@require_POST
def remove_from_wishlist_view(request, product_id):
    """
    URL:
      path("wishlist/items/remove/<int:product_id>/", remove_from_wishlist_view, name="wishlist_remove")
    """
    wishlist, _created = Wishlist.objects.get_or_create(user=request.user)

    deleted, _ = WishlistItem.objects.filter(
        wishlist=wishlist,
        product_id=product_id,
    ).delete()

    if deleted:
        messages.success(request, _("Produit retiré de votre liste de souhaits."))
    else:
        messages.info(request, _("Ce produit n'était pas dans votre liste de souhaits."))

    return redirect(
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("economic:ecommerce:wishlist")
    )




# # economic/ecommerce/views/wishlist.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render

# from ..models.wishlist import Wishlist
# from ..models.wishlist_item import WishlistItem
# from ..models.product import Product


# @login_required
# def wishlist_view(request):
#     wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
#     return render(request, "ecommerce/wishlist.html", {"wishlist": wishlist})


# @login_required
# def add_to_wishlist_view(request, product_id):
#     wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
#     product = get_object_or_404(Product, id=product_id, is_active=True)

#     WishlistItem.objects.get_or_create(
#         wishlist=wishlist,
#         product=product,
#     )
#     return redirect("ecommerce:wishlist")


# @login_required
# def remove_from_wishlist_view(request, product_id):
#     wishlist = get_object_or_404(Wishlist, user=request.user)
#     WishlistItem.objects.filter(
#         wishlist=wishlist,
#         product_id=product_id,
#     ).delete()
#     return redirect("ecommerce:wishlist")
