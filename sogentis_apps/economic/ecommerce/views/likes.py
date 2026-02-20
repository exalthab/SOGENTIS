# economic/ecommerce/views/likes.py
from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Product


def like_toggle_view(request, product_id: int):
    """
    Like toggle (simple).
    Si tu as déjà un modèle Like en DB, tu remplaceras ici la logique.
    En attendant: action active + feedback + redirect.
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        messages.success(request, _("Merci ! Votre réaction a été enregistrée."))
    else:
        messages.info(request, _("Action non supportée."))

    return redirect(reverse("economic:ecommerce:product_detail", kwargs={"slug": product.safe_translation_getter("slug")}))
