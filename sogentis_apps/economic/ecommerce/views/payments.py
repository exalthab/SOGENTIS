# economic/ecommerce/views/payments.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models.order import Order


@login_required
def choose_payment_view(request, uuid):
    """
    URL:
      path("payments/choose/<uuid:uuid>/", choose_payment_view, name="choose_payment")
    """
    order = get_object_or_404(Order, uuid=uuid, user=request.user)

    # Optionnel : empêcher choix si déjà payée
    if getattr(order, "is_paid", False):
        messages.info(request, _("Cette commande est déjà payée."))
        return redirect("economic:ecommerce:order_detail", uuid=order.uuid)

    payment_methods = [
        {
            "label": "💳 Stripe",
            "action_url": reverse(
                "economic:ecommerce:payment_checkout",
                kwargs={"provider": "stripe", "uuid": order.uuid},
            ),
            "description": _("Payer par carte bancaire via Stripe."),
        },
        {
            "label": "🅿️ PayPal",
            "action_url": reverse(
                "economic:ecommerce:payment_checkout",
                kwargs={"provider": "paypal", "uuid": order.uuid},
            ),
            "description": _("Payer avec votre compte PayPal."),
        },
        {
            "label": "📱 Mobile Money",
            "action_url": reverse(
                "economic:ecommerce:payment_checkout",
                kwargs={"provider": "mobilemoney", "uuid": order.uuid},
            ),
            "description": _("Orange Money, Wave, etc."),
        },
    ]

    payment_note = _("Le paiement est traité par le prestataire. Une confirmation sera appliquée à la commande après retour ou webhook.")

    return render(
        request,
        "economic/ecommerce/payments/choose_payment.html",
        {"order": order, "payment_methods": payment_methods, "payment_note": payment_note},
    )


@require_POST
@login_required
def provider_checkout_view(request, provider, uuid):
    """
    URL:
      path("payments/<str:provider>/<uuid:uuid>/", provider_checkout_view, name="payment_checkout")

    POST attendu (depuis choose_payment).
    """
    order = get_object_or_404(Order, uuid=uuid, user=request.user)

    if getattr(order, "is_paid", False):
        messages.info(request, _("Cette commande est déjà payée."))
        return redirect("economic:ecommerce:order_detail", uuid=order.uuid)

    provider_display_name = {
        "stripe": "Stripe",
        "paypal": "PayPal",
        "mobilemoney": _("Mobile Money"),
    }.get(provider, provider)

    # ✅ Placeholder propre (production-safe)
    # Ici: créer session/provider checkout, puis mettre redirect_url (Stripe Checkout Session / PayPal Approval URL / etc.)
    redirect_url = None
    instructions = None

    messages.warning(
        request,
        _("Le prestataire %(p)s n'est pas encore configuré. Choisissez un autre moyen de paiement.")
        % {"p": provider_display_name},
    )
    return render(
        request,
        "economic/ecommerce/payments/checkout_provider.html",
        {
            "order": order,
            "provider": provider,
            "provider_display_name": provider_display_name,
            "redirect_url": redirect_url,
            "instructions": instructions,
        },
    )


@csrf_exempt
def webhook_generic_view(request, provider):
    """
    URL:
      path("payments/webhook/<str:provider>/", webhook_generic_view, name="payment_webhook")

    IMPORTANT: webhook -> csrf_exempt obligatoire.
    TODO: vérifier signature provider + mettre à jour Order (paid/failed).
    """
    return HttpResponse("OK", status=200)







# # economic/ecommerce/views/payments.py
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
# from django.utils.translation import gettext as _
# from django.views.decorators.csrf import csrf_exempt

# from ..models.order import Order


# @login_required
# def choose_payment_view(request, uuid):
#     """
#     URL:
#       path("payments/choose/<uuid:uuid>/", choose_payment_view, name="choose_payment")
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     payment_methods = [
#         {
#             "label": "💳 Stripe",
#             "action_url": reverse("economic:ecommerce:payment_checkout", kwargs={"provider": "stripe", "uuid": order.uuid}),
#             "description": _("Payer par carte bancaire via Stripe."),
#         },
#         {
#             "label": "🅿️ PayPal",
#             "action_url": reverse("economic:ecommerce:payment_checkout", kwargs={"provider": "paypal", "uuid": order.uuid}),
#             "description": _("Payer avec votre compte PayPal."),
#         },
#         {
#             "label": "📱 Mobile Money",
#             "action_url": reverse("economic:ecommerce:payment_checkout", kwargs={"provider": "mobilemoney", "uuid": order.uuid}),
#             "description": _("Orange Money, Wave, etc."),
#         },
#     ]

#     return render(
#         request,
#         "economic/ecommerce/payments/choose_payment.html",
#         {"order": order, "payment_methods": payment_methods},
#     )


# @login_required
# def provider_checkout_view(request, provider, uuid):
#     """
#     URL:
#       path("payments/<str:provider>/<uuid:uuid>/", provider_checkout_view, name="payment_checkout")
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     provider_display_name = {
#         "stripe": "Stripe",
#         "paypal": "PayPal",
#         "mobilemoney": _("Mobile Money"),
#     }.get(provider, provider)

#     # TODO: ici tu crées une session/provider checkout et tu donnes redirect_url
#     redirect_url = None

#     return render(
#         request,
#         "economic/ecommerce/payments/checkout_provider.html",
#         {
#             "order": order,
#             "provider": provider,
#             "provider_display_name": provider_display_name,
#             "redirect_url": redirect_url,
#         },
#     )


# @csrf_exempt
# def webhook_generic_view(request, provider):
#     """
#     URL:
#       path("payments/webhook/<str:provider>/", webhook_generic_view, name="payment_webhook")

#     IMPORTANT: webhook -> csrf_exempt obligatoire.
#     TODO: vérifier signature provider + mettre à jour Order (paid/failed).
#     """
#     return HttpResponse("OK", status=200)





# import json
# from decimal import Decimal

# from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.translation import gettext_lazy as _

# from ..models.order import Order
# from ..models.payment_transaction import PaymentTransaction
# from ..services.payment_service import (
#     initiate_payment,
#     apply_webhook_event,
# )


# @login_required
# def choose_payment_view(request, uuid):
#     """
#     Étape intermédiaire : choisir le moyen de paiement pour une commande.
#     UUID = identifiant public de la commande.
#     """
#     order = get_object_or_404(
#         Order,
#         uuid=uuid,
#         user=request.user,
#     )

#     # Liste des providers affichés sur la page
#     payment_providers = [
#         {
#             "code": "stripe",
#             "label": _("Carte bancaire (Stripe)"),
#             "description": _("Payer par carte bancaire de manière sécurisée."),
#         },
#         {
#             "code": "paypal",
#             "label": "PayPal",
#             "description": _("Payer avec votre compte PayPal."),
#         },
#         # Tu pourras ajouter "wave", "orange_money", etc. ici plus tard.
#     ]

#     context = {
#         "order": order,
#         "payment_providers": payment_providers,
#     }
#     return render(request, "economic/ecommerce/payments/choose_payment.html", context)

# # =====================================================
# # CHECKOUT PROVIDER (PLACEHOLDER)
# # =====================================================
# def provider_checkout_view(request, provider: str, uuid):
#     """
#     Page de checkout “placeholder”.
#     Cette vue est VOLONTAIREMENT simple.

#     👉 En prod réelle :
#        - Stripe : redirection Checkout Session
#        - PayPal : redirect approve_url
#        - Wave / OM : redirect gateway
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     # Sécurité : pas de paiement sur commande non éditable
#     if not order.is_editable:
#         return HttpResponseBadRequest(_("Cette commande ne peut plus être payée"))

#     # Crée la transaction (audit)
#     tx = initiate_payment(order, provider)

#     context = {
#         "order": order,
#         "provider": provider,
#         "payment": tx,
#     }
#     return render(
#         request,
#         "economic/ecommerce/payments/checkout_provider.html",
#         context,
#     )


# # =====================================================
# # WEBHOOK GÉNÉRIQUE
# # =====================================================
# @csrf_exempt
# def webhook_generic_view(request, provider: str):
#     """
#     Webhook générique (structure commune).
#     ⚠️ En production :
#        - vérifier la signature (Stripe-Signature, PayPal transmission_id, etc.)
#        - mapper le payload EXACT du provider
#     """
#     if request.method != "POST":
#         return HttpResponseBadRequest("invalid_method")

#     try:
#         payload = json.loads(request.body.decode("utf-8") or "{}")
#     except Exception:
#         return HttpResponseBadRequest("invalid_json")

#     # ==========================
#     # EXTRACTION MINIMALE
#     # (à adapter par provider réel)
#     # ==========================
#     event_id = str(payload.get("event_id", "")).strip()
#     order_uuid = str(payload.get("order_uuid", "")).strip()
#     provider_payment_id = str(payload.get("payment_id", "")).strip()
#     currency = str(payload.get("currency", "XOF")).strip()

#     try:
#         amount = Decimal(str(payload.get("amount", "0")))
#     except Exception:
#         return HttpResponseBadRequest("invalid_amount")

#     status = str(payload.get("status", "")).lower()

#     if not event_id or not order_uuid:
#         return HttpResponseBadRequest("missing_fields")

#     # ==========================
#     # DÉTERMINER SUCCÈS
#     # ==========================
#     succeeded = status in {
#         PaymentTransaction.STATUS_SUCCEEDED,
#         "paid",
#         "success",
#         "completed",
#     }

#     # ==========================
#     # APPLIQUER L’ÉVÉNEMENT
#     # ==========================
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
