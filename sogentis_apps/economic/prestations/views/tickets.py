# economic/prestations/views/tickets.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from ..forms import PrestationRequestForm
try:
    from ..models import PrestationRequest  # type: ignore
except Exception:
    from ..models.prestations_request import PrestationRequest  # type: ignore


def _model_field_names(model) -> set[str]:
    try:
        return {f.name for f in model._meta.get_fields()}
    except Exception:
        return set()


def _safe_select_related(qs, *fields: str):
    available = _model_field_names(qs.model)
    keep = [f for f in fields if f in available]
    return qs.select_related(*keep) if keep else qs


@login_required
def tickets_view(request):
    if request.method == "POST":
        form = PrestationRequestForm(request.POST)
        if form.is_valid():
            ticket: PrestationRequest = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, _("Votre demande a été envoyée."))
            return redirect("economic:prestations:tickets")
    else:
        form = PrestationRequestForm()

    tickets_qs = PrestationRequest.objects.filter(user=request.user)
    tickets_qs = _safe_select_related(tickets_qs, "prestation", "package")
    tickets_qs = tickets_qs.order_by("-created_at", "-id")

    return render(
        request,
        "economic/prestations/tickets.html",
        {
            "cur": (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper(),
            "form": form,
            "tickets": tickets_qs,
        },
    )







# # economic/prestations/views/tickets.py - good
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from ..models.prestations_request import PrestationRequest
# from ..forms import PrestationRequestForm


# @login_required
# def tickets_view(request):
#     """
#     Page /economic/prestations/tickets/
#     - Formulaire nouvelle demande (prestation OU pack selon ton modèle)
#     - Liste les demandes de l'utilisateur connecté
#     """
#     if request.method == "POST":
#         form = PrestationRequestForm(request.POST)
#         if form.is_valid():
#             ticket: PrestationRequest = form.save(commit=False)
#             ticket.user = request.user
#             ticket.save()
#             messages.success(request, _("Votre demande a été envoyée."))
#             return redirect("economic:prestations:tickets")
#     else:
#         form = PrestationRequestForm()

#     tickets_qs = (
#         PrestationRequest.objects.filter(user=request.user)
#         .select_related("prestation", "package")
#         .order_by("-created_at", "-id")
#     )

#     return render(
#         request,
#         "economic/prestations/tickets.html",
#         {
#             "form": form,
#             "tickets": tickets_qs,
#         },
#     )





# # economic/prestations/views/tickets.py

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages

# from ..models.prestations_request import ServiceRequest
# from ..forms import ServiceRequestForm


# @login_required
# def tickets_view(request):
#     """
#     Page /economic/services/tickets/
#     - Affiche le formulaire de nouvelle demande
#     - Liste les demandes de l'utilisateur connecté
#     """
#     if request.method == "POST":
#         form = ServiceRequestForm(request.POST)
#         if form.is_valid():
#             service_request = form.save(commit=False)
#             service_request.user = request.user
#             service_request.save()
#             messages.success(request, "Votre demande a été envoyée.")
#             return redirect("economic:services:tickets")
#     else:
#         form = ServiceRequestForm()

#     tickets_qs = ServiceRequest.objects.filter(user=request.user).select_related("service").order_by("-created_at")

#     context = {
#         "form": form,
#         "tickets": tickets_qs,
#     }
#     return render(request, "economic/services/tickets.html", context)





# # economic/services/views/tickets.py
# from django.shortcuts import render

# def tickets_view(request):
#     return render(request, "services/tickets.html")
