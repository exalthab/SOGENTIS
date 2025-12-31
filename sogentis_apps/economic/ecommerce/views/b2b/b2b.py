# views/b2b.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from economic.decorators import b2b_required
from economic.ecommerce.models import Product
from economic.ecommerce.services import create_quote


@login_required
@b2b_required
def request_quote_view(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if request.method == "POST":
        create_quote(
            request.user,
            product,
            request.POST
        )
        return redirect("economic:ecommerce:b2b_thanks")

    context = {
        "product": product,
    }

    return render(
        request,
        "economic/ecommerce/b2b/quote_request.html",
        context,
    )
