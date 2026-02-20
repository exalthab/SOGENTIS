# payments/views/checkout.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from payments.models import PaymentIntent


@login_required
def checkout_view(request, uuid):
    intent = get_object_or_404(PaymentIntent, uuid=uuid)

    # Sécurité: l'intent appartient au user (ou staff)
    if intent.user_id != request.user.id and not request.user.is_staff:
        raise Http404()

    if not intent.is_payable:
        messages.error(request, _("Montant invalide."))
        return redirect(intent.cancel_url or "/")

    # Déjà payé
    if intent.status == PaymentIntent.Status.PAID:
        messages.info(request, _("Paiement déjà validé."))
        return redirect(intent.return_url or "/")

    return render(
        request,
        "payments/checkout.html",
        {
            "intent": intent,
        },
    )


@login_required
def success_view(request, uuid):
    intent = get_object_or_404(PaymentIntent, uuid=uuid)
    if intent.user_id != request.user.id and not request.user.is_staff:
        raise Http404()
    return redirect(intent.return_url or "/")


@login_required
def cancel_view(request, uuid):
    intent = get_object_or_404(PaymentIntent, uuid=uuid)
    if intent.user_id != request.user.id and not request.user.is_staff:
        raise Http404()
    return redirect(intent.cancel_url or "/")
