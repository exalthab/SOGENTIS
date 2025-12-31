# economic/services/views/request_quote.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models.service import Service
from ..models.service_request import ServiceRequest
from ..forms import QuoteRequestForm


@login_required
def request_quote_view(request, slug):
    """
    Page /economic/services/<slug>/quote/
    - Demande de devis pour un service précis.
    """
    service = get_object_or_404(Service, slug=slug, is_active=True)

    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            sr = form.save(commit=False)
            sr.user = request.user
            sr.service = service
            sr.save()
            messages.success(request, "Votre demande de devis a été envoyée.")
            return redirect("economic:services:detail", slug=service.slug)
    else:
        form = QuoteRequestForm()

    context = {
        "service": service,
        "form": form,
    }
    return render(request, "economic/services/quote_form.html", context)






# # economic/services/views/request_quote.py
# from django.shortcuts import render

# def request_quote_view(request):
#     return render(request, "services/request_quote.html")
