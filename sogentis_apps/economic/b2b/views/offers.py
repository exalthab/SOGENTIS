# economic/b2b/views/offers.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from economic.b2b.forms import OfferForm
from economic.b2b.models import RFQ, Offer


@login_required
def offer_create_view(request, rfq_id: int):
    """
    Supplier-side minimal: user authentifié peut soumettre une offre.
    """
    rfq = get_object_or_404(RFQ, pk=rfq_id)

    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            offer: Offer = form.save(commit=False)
            offer.rfq = rfq
            offer.supplier = request.user
            offer.save()
            messages.success(request, "Offre soumise.")
            return redirect("economic:b2b:offer_create", rfq_id=rfq.id)
    else:
        form = OfferForm()

    return render(request, "economic/b2b/offers/offer_form.html", {"rfq": rfq, "form": form})
