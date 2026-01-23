# economic/ecommerce/views/favorites_list.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models.favorite import Favorite


@login_required
def favorites_list_view(request):
    favorites = (
        Favorite.objects
        .filter(user=request.user)
        .select_related("product", "product__category", "product__vendor")
        .prefetch_related("product__images")
        .order_by("-created_at")
    )

    return render(
        request,
        "economic/ecommerce/favorites/favorites_list.html",
        {"favorites": favorites},
    )
