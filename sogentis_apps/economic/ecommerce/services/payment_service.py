"""
Service générique de paiement (abstraction).

- Crée une transaction de paiement (audit)
- Gère l'idempotence via provider_event_id
- Applique les webhooks
- Marque la commande comme payée si succès
"""

from decimal import Decimal
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from ..models.order import Order
from ..models.payment_transactions import PaymentTransaction

from ..services.invoice_service import generate_invoice_pdf

# ==========================
# CONSTANTES
# ==========================
ALLOWED_PROVIDERS = {
    PaymentTransaction.PROVIDER_STRIPE,
    PaymentTransaction.PROVIDER_PAYPAL,
    PaymentTransaction.PROVIDER_WAVE,
    PaymentTransaction.PROVIDER_ORANGE,
}


# ==========================
# INITIATION DU PAIEMENT
# ==========================
def initiate_payment(order: Order, provider: str) -> PaymentTransaction:
    """
    Crée une transaction de paiement à l'état 'initiated'
    et retourne l'objet PaymentTransaction.
    """
    provider = (provider or "").strip().lower()

    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(_("Prestataire de paiement inconnu"))

    if not order.is_editable:
        raise ValueError(_("Cette commande ne peut plus être payée"))

    tx = PaymentTransaction.objects.create(
        order=order,
        provider=provider,
        status=PaymentTransaction.STATUS_INITIATED,
        amount=order.total_amount,
        currency="XOF",
    )

    return tx


# ==========================
# MARQUER COMMANDE PAYÉE
# ==========================
@transaction.atomic
def mark_order_paid(order: Order):
    """
    Marque une commande comme payée (sécurisé, idempotent).
    """
    if order.status == Order.STATUS_PAID:
        return

    order.status = Order.STATUS_PAID
    order.save(update_fields=["status"])
    
       # 🔥 Génération automatique de la facture
    generate_invoice_pdf(order)


# ==========================
# WEBHOOK / ÉVÉNEMENT PROVIDER
# ==========================
@transaction.atomic
def apply_webhook_event(
    *,
    provider: str,
    event_id: str,
    provider_payment_id: str,
    order_uuid: str,
    amount,
    currency: str,
    raw_payload: dict,
    succeeded: bool,
) -> PaymentTransaction:
    """
    Applique un événement webhook provenant d'un prestataire.

    - idempotence par provider_event_id
    - vérification du montant
    - mise à jour commande si succès
    """

    provider = (provider or "").strip().lower()

    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(_("Prestataire de paiement inconnu"))

    # 🔒 Idempotence stricte (event_id unique)
    tx, created = PaymentTransaction.objects.get_or_create(
        provider_event_id=event_id,
        defaults={
            "provider": provider,
            "provider_payment_id": provider_payment_id or "",
            "amount": Decimal(amount),
            "currency": currency or "XOF",
            "payload": raw_payload or {},
            "status": PaymentTransaction.STATUS_PENDING,
        },
    )

    if not created:
        return tx  # événement déjà traité

    # 🔐 Lock commande
    order = Order.objects.select_for_update().get(uuid=order_uuid)

    # 🔍 Vérification montant
    if Decimal(order.total_amount) != Decimal(amount):
        tx.order = order
        tx.status = PaymentTransaction.STATUS_FAILED
        tx.payload = {
            **(tx.payload or {}),
            "error": "amount_mismatch",
            "expected": str(order.total_amount),
            "received": str(amount),
        }
        tx.save(update_fields=["order", "status", "payload"])
        return tx

    # 🔁 Lier la transaction à la commande
    tx.order = order
    tx.status = (
        PaymentTransaction.STATUS_SUCCEEDED
        if succeeded
        else PaymentTransaction.STATUS_FAILED
    )
    tx.save(update_fields=["order", "status"])

    # ✅ Paiement validé → commande payée
    if succeeded:
        mark_order_paid(order)

    return tx






# # economic/ecommerce/services/payment_service.py
# """
# Service générique de paiement (abstraction).
# Ici on ne configure pas Stripe/PayPal encore: on prépare les redirects
# et les points d’entrée (checkout pages) pour chaque provider.
# """

# from django.db import transaction
# from django.utils.translation import gettext_lazy as _

# from ..models.order import Order
# from ..models.payment_transaction import PaymentTransaction


# def initiate_payment(order: Order, provider: str) -> str:
#     provider = (provider or "").strip().lower()
#     if provider not in {"stripe", "paypal", "wave", "orange"}:
#         raise ValueError(_("Provider de paiement inconnu"))

#     # créer transaction "initiated" (audit)
#     PaymentTransaction.objects.create(
#         order=order,
#         provider=provider,
#         status="initiated",
#         amount=order.total_amount,
#         currency="XOF",
#     )

#     # endpoints “checkout provider” (étape suivante: intégrations réelles)
#     return f"/payments/{provider}/{order.uuid}/"


# @transaction.atomic
# def mark_order_paid(order: Order):
#     # sécurité: ne pas repayer une commande déjà payée
#     if order.status == "paid":
#         return
#     order.status = "paid"
#     order.save(update_fields=["status"])


# @transaction.atomic
# def apply_webhook_event(
#     *,
#     provider: str,
#     event_id: str,
#     provider_payment_id: str,
#     order_uuid: str,
#     amount,
#     currency: str,
#     raw_payload: dict,
#     succeeded: bool,
# ):
#     # idempotence par event_id
#     tx, created = PaymentTransaction.objects.get_or_create(
#         provider_event_id=event_id,
#         defaults={
#             "provider": provider,
#             "provider_payment_id": provider_payment_id or "",
#             "amount": amount,
#             "currency": currency or "XOF",
#             "payload": raw_payload or {},
#             "status": "pending",
#             "order_id": None,  # fixé ensuite
#         },
#     )
#     if not created:
#         return tx  # déjà traité

#     order = Order.objects.select_for_update().get(uuid=order_uuid)

#     # sécurité montant/devise
#     if str(order.total_amount) != str(amount):
#         tx.status = "failed"
#         tx.payload = {**(tx.payload or {}), "error": "amount_mismatch"}
#         tx.order = order
#         tx.save(update_fields=["status", "payload", "order"])
#         return tx

#     tx.order = order
#     tx.status = "succeeded" if succeeded else "failed"
#     tx.save(update_fields=["order", "status"])

#     if succeeded:
#         mark_order_paid(order)

#     return tx
