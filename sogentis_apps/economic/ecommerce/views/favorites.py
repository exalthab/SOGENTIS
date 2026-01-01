# economic/ecommerce/views/favorites.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from ..models.product import Product
from ..models.favorite import Favorite


@login_required
@require_POST
def favorite_toggle_view(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if created:
        is_favorited = True
    else:
        fav.delete()
        is_favorited = False

    fav_count = Favorite.objects.filter(user=request.user).count()

    # AJAX ?
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {"ok": True, "favorited": is_favorited, "count": fav_count}
        )

    # Fallback classic (safe next)
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    slug_any = product.safe_translation_getter("slug", any_language=True)
    if slug_any:
        return redirect(reverse("economic:ecommerce:product_detail", args=[slug_any]))

    return redirect(reverse("economic:ecommerce:index"))
