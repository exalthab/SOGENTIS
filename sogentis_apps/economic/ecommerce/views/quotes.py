# economic/ecommerce/views/quotes.py
from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Product


def request_quote_view(request, product_id: int):
    """
    Demande de devis (B2B).
    Ici, on garde volontairement simple:
    - on valide le produit
    - on redirige vers la page produit (ou une page devis si tu en as une)
    """
    product = get_object_or_404(Product, pk=product_id)

    messages.info(request, _("Votre demande de devis a été prise en compte. Nous vous contacterons rapidement."))
    return redirect(reverse("economic:ecommerce:product_detail", kwargs={"slug": product.safe_translation_getter("slug")}))
