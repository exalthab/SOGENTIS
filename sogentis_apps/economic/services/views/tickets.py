# economic/services/views/tickets.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models.service_request import ServiceRequest
from ..forms import ServiceRequestForm


@login_required
def tickets_view(request):
    """
    Page /economic/services/tickets/
    - Affiche le formulaire de nouvelle demande
    - Liste les demandes de l'utilisateur connecté
    """
    if request.method == "POST":
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.save()
            messages.success(request, "Votre demande a été envoyée.")
            return redirect("economic:services:tickets")
    else:
        form = ServiceRequestForm()

    tickets_qs = ServiceRequest.objects.filter(user=request.user).select_related("service").order_by("-created_at")

    context = {
        "form": form,
        "tickets": tickets_qs,
    }
    return render(request, "economic/services/tickets.html", context)





# # economic/services/views/tickets.py
# from django.shortcuts import render

# def tickets_view(request):
#     return render(request, "services/tickets.html")
