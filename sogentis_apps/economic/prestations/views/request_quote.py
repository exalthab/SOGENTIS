# economic/prestations/views/request_quote.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from ..forms import QuoteRequestForm
from ..models import Prestation
try:
    from ..models import PrestationRequest  # type: ignore
except Exception:
    from ..models.prestations_request import PrestationRequest  # type: ignore


@login_required
def request_quote_view(request, slug: str):
    prestation = get_object_or_404(Prestation, slug=slug, is_active=True)

    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            pr: PrestationRequest = form.save(commit=False)
            pr.user = request.user

            if hasattr(pr, "prestation"):
                pr.prestation = prestation
            if hasattr(pr, "package"):
                pr.package = None

            pr.save()
            messages.success(request, _("Votre demande de devis a été envoyée."))
            return redirect("economic:prestations:detail", slug=prestation.slug)
    else:
        form = QuoteRequestForm()

    return render(
        request,
        "economic/prestations/quote_form.html",
        {
            "cur": (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper(),
            "prestation": prestation,
            "form": form,
        },
    )







# # economic/prestations/views/request_quote.py - good
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext_lazy as _

# from ..models import Prestation
# from ..models.prestations_request import PrestationRequest
# from ..forms import QuoteRequestForm


# @login_required
# def request_quote_view(request, slug: str):
#     """
#     Page /economic/prestations/<slug>/quote/
#     - Demande de devis pour une prestation précise.
#     - On enregistre dans PrestationRequest (prestation OU pack).
#     """
#     prestation = get_object_or_404(Prestation, slug=slug, is_active=True)

#     if request.method == "POST":
#         form = QuoteRequestForm(request.POST)
#         if form.is_valid():
#             pr: PrestationRequest = form.save(commit=False)
#             pr.user = request.user
#             pr.prestation = prestation
#             pr.save()

#             messages.success(request, _("Votre demande de devis a été envoyée."))
#             return redirect("economic:prestations:detail", slug=prestation.slug)
#     else:
#         form = QuoteRequestForm()

#     return render(
#         request,
#         "economic/prestations/package_quote_form.html",
#         {
#             "prestation": prestation,
#             # compat si un template attend encore "service"
#             "service": prestation,
#             "form": form,
#         },
#     )






# # economic/prestations/views/request_quote.py

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages

# from ..models.prestations import Service
# from ..models.prestations_request import ServiceRequest
# from ..forms import QuoteRequestForm


# @login_required
# def request_quote_view(request, slug):
#     """
#     Page /economic/services/<slug>/quote/
#     - Demande de devis pour un service précis.
#     """
#     service = get_object_or_404(Service, slug=slug, is_active=True)

#     if request.method == "POST":
#         form = QuoteRequestForm(request.POST)
#         if form.is_valid():
#             sr = form.save(commit=False)
#             sr.user = request.user
#             sr.service = service
#             sr.save()
#             messages.success(request, "Votre demande de devis a été envoyée.")
#             return redirect("economic:services:detail", slug=service.slug)
#     else:
#         form = QuoteRequestForm()

#     context = {
#         "service": service,
#         "form": form,
#     }
#     return render(request, "economic/services/quote_form.html", context)






# # economic/services/views/request_quote.py
# from django.shortcuts import render

# def request_quote_view(request):
#     return render(request, "services/request_quote.html")
