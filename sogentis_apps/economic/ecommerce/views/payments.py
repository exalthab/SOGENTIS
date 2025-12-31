import json
from decimal import Decimal

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _

from ..models.order import Order
from ..models.payment_transaction import PaymentTransaction
from ..services.payment_service import (
    initiate_payment,
    apply_webhook_event,
)


@login_required
def choose_payment_view(request, uuid):
    """
    Étape intermédiaire : choisir le moyen de paiement pour une commande.
    UUID = identifiant public de la commande.
    """
    order = get_object_or_404(
        Order,
        uuid=uuid,
        user=request.user,
    )

    # Liste des providers affichés sur la page
    payment_providers = [
        {
            "code": "stripe",
            "label": _("Carte bancaire (Stripe)"),
            "description": _("Payer par carte bancaire de manière sécurisée."),
        },
        {
            "code": "paypal",
            "label": "PayPal",
            "description": _("Payer avec votre compte PayPal."),
        },
        # Tu pourras ajouter "wave", "orange_money", etc. ici plus tard.
    ]

    context = {
        "order": order,
        "payment_providers": payment_providers,
    }
    return render(request, "economic/ecommerce/payments/choose_payment.html", context)

# =====================================================
# CHECKOUT PROVIDER (PLACEHOLDER)
# =====================================================
def provider_checkout_view(request, provider: str, uuid):
    """
    Page de checkout “placeholder”.
    Cette vue est VOLONTAIREMENT simple.

    👉 En prod réelle :
       - Stripe : redirection Checkout Session
       - PayPal : redirect approve_url
       - Wave / OM : redirect gateway
    """
    order = get_object_or_404(Order, uuid=uuid, user=request.user)

    # Sécurité : pas de paiement sur commande non éditable
    if not order.is_editable:
        return HttpResponseBadRequest(_("Cette commande ne peut plus être payée"))

    # Crée la transaction (audit)
    tx = initiate_payment(order, provider)

    context = {
        "order": order,
        "provider": provider,
        "payment": tx,
    }
    return render(
        request,
        "economic/ecommerce/payments/checkout_provider.html",
        context,
    )


# =====================================================
# WEBHOOK GÉNÉRIQUE
# =====================================================
@csrf_exempt
def webhook_generic_view(request, provider: str):
    """
    Webhook générique (structure commune).
    ⚠️ En production :
       - vérifier la signature (Stripe-Signature, PayPal transmission_id, etc.)
       - mapper le payload EXACT du provider
    """
    if request.method != "POST":
        return HttpResponseBadRequest("invalid_method")

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return HttpResponseBadRequest("invalid_json")

    # ==========================
    # EXTRACTION MINIMALE
    # (à adapter par provider réel)
    # ==========================
    event_id = str(payload.get("event_id", "")).strip()
    order_uuid = str(payload.get("order_uuid", "")).strip()
    provider_payment_id = str(payload.get("payment_id", "")).strip()
    currency = str(payload.get("currency", "XOF")).strip()

    try:
        amount = Decimal(str(payload.get("amount", "0")))
    except Exception:
        return HttpResponseBadRequest("invalid_amount")

    status = str(payload.get("status", "")).lower()

    if not event_id or not order_uuid:
        return HttpResponseBadRequest("missing_fields")

    # ==========================
    # DÉTERMINER SUCCÈS
    # ==========================
    succeeded = status in {
        PaymentTransaction.STATUS_SUCCEEDED,
        "paid",
        "success",
        "completed",
    }

    # ==========================
    # APPLIQUER L’ÉVÉNEMENT
    # ==========================
    apply_webhook_event(
        provider=provider,
        event_id=event_id,
        provider_payment_id=provider_payment_id,
        order_uuid=order_uuid,
        amount=amount,
        currency=currency,
        raw_payload=payload,
        succeeded=succeeded,
    )

    return JsonResponse({"ok": True})







# # economic/ecommerce/views/payments.py
# import json
# from decimal import Decimal

# from django.conf import settings
# from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
# from django.shortcuts import get_object_or_404, redirect, render
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.translation import gettext_lazy as _

# from ..models.order import Order
# from ..services.payment_service import apply_webhook_event


# def _dummy_checkout(request, provider: str, uuid):
#     """
#     Page de checkout “placeholder”.
#     À l’étape d’intégration réelle, tu remplaceras par Stripe Checkout / PayPal etc.
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     return render(request, "ecommerce/payments/checkout_provider.html", {"order": order, "provider": provider})


# @csrf_exempt
# def webhook_generic(request, provider: str):
#     """
#     Webhook générique (structure). À adapter par provider.
#     IMPORTANT: en prod, valide la signature (Stripe: Stripe-Signature, etc.)
#     """
#     if request.method != "POST":
#         return HttpResponseBadRequest("invalid_method")

#     try:
#         payload = json.loads(request.body.decode("utf-8") or "{}")
#     except Exception:
#         return HttpResponseBadRequest("invalid_json")

#     # ⚠️ Structure attendue (à mapper par provider réel)
#     event_id = str(payload.get("event_id", "")).strip()
#     order_uuid = str(payload.get("order_uuid", "")).strip()
#     provider_payment_id = str(payload.get("payment_id", "")).strip()
#     currency = str(payload.get("currency", "XOF")).strip()
#     amount = Decimal(str(payload.get("amount", "0")))
#     status = str(payload.get("status", "")).lower()

#     if not event_id or not order_uuid:
#         return HttpResponseBadRequest("missing_fields")

#     succeeded = status in {"succeeded", "paid", "success"}

#     apply_webhook_event(
#         provider=provider,
#         event_id=event_id,
#         provider_payment_id=provider_payment_id,
#         order_uuid=order_uuid,
#         amount=amount,
#         currency=currency,
#         raw_payload=payload,
#         succeeded=succeeded,
#     )
#     return JsonResponse({"ok": True})
