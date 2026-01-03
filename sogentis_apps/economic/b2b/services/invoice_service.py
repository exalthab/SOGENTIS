# economic/b2b/services/invoice_service.py
from django.db import transaction, IntegrityError
from django.utils import timezone

from economic.b2b.models import Invoice, BulkOrder


def _next_invoice_number() -> str:
    """
    Format: INV-YYYY-000001
    (simple, stable en prod)
    """
    year = timezone.now().year
    prefix = f"INV-{year}-"

    last = (
        Invoice.objects
        .filter(invoice_number__startswith=prefix)
        .order_by("-invoice_number")
        .values_list("invoice_number", flat=True)
        .first()
    )
    if not last:
        return f"{prefix}000001"

    try:
        seq = int(last.split("-")[-1]) + 1
    except Exception:
        seq = 1

    return f"{prefix}{seq:06d}"


@transaction.atomic
def create_invoice_for_bulk_order(bulk_order: BulkOrder, *, issue: bool = True) -> Invoice:
    """
    Crée une facture pour une bulk_order (OneToOne).
    Synchronise le montant depuis la commande.
    """
    bulk_order.recalc_total(save=True)

    if hasattr(bulk_order, "invoice") and bulk_order.invoice_id:
        inv = bulk_order.invoice
        inv.sync_amount_from_order(save=True)
        return inv

    for _ in range(5):
        number = _next_invoice_number()
        try:
            inv = Invoice.objects.create(
                bulk_order=bulk_order,
                invoice_number=number,
                amount=bulk_order.total_amount,
                status=Invoice.Status.DRAFT,
            )
            if issue:
                inv.mark_issued()
            return inv
        except IntegrityError:
            continue

    raise IntegrityError("Impossible de générer un numéro de facture unique.")






# # economic/b2b/services/invoice_service.py
# from django.db import IntegrityError, transaction
# from django.utils import timezone

# from economic.b2b.models import BulkOrder, Invoice


# def _next_invoice_number() -> str:
#     year = timezone.now().year
#     prefix = f"INV-{year}-"

#     last = (
#         Invoice.objects.filter(invoice_number__startswith=prefix)
#         .order_by("-invoice_number")
#         .values_list("invoice_number", flat=True)
#         .first()
#     )

#     if not last:
#         return f"{prefix}000001"

#     try:
#         seq = int(last.split("-")[-1]) + 1
#     except Exception:
#         seq = 1

#     return f"{prefix}{seq:06d}"


# def create_invoice_for_bulk_order(order: BulkOrder) -> Invoice:
#     """
#     Crée une facture si absente, et met la BulkOrder en 'invoiced'.
#     Sécurisé en prod (atomic + lock).
#     """
#     # ✅ accès safe au OneToOne
#     existing = getattr(order, "invoice", None)
#     if existing:
#         return existing

#     for _ in range(5):
#         number = _next_invoice_number()
#         try:
#             with transaction.atomic():
#                 # ✅ lock commande pour éviter double création concurrente
#                 locked = BulkOrder.objects.select_for_update().get(pk=order.pk)

#                 # re-check après lock
#                 existing2 = getattr(locked, "invoice", None)
#                 if existing2:
#                     return existing2

#                 inv = Invoice.objects.create(
#                     bulk_order=locked,
#                     invoice_number=number,
#                     status="draft",
#                     amount=locked.total_amount,
#                 )

#                 if locked.status != "invoiced":
#                     locked.status = "invoiced"
#                     locked.save(update_fields=["status", "updated_at"] if hasattr(locked, "updated_at") else ["status"])

#                 return inv
#         except IntegrityError:
#             continue

#     # fallback (très rare)
#     inv = Invoice.objects.create(
#         bulk_order=order,
#         invoice_number=_next_invoice_number(),
#         status="draft",
#         amount=order.total_amount,
#     )
#     if order.status != "invoiced":
#         order.status = "invoiced"
#         order.save(update_fields=["status", "updated_at"] if hasattr(order, "updated_at") else ["status"])
#     return inv


# def mark_invoice_issued(invoice: Invoice) -> Invoice:
#     """
#     Marque une facture comme émise + date d’émission.
#     Synchronise amount avec la commande (si besoin).
#     """
#     invoice.status = "issued"
#     invoice.issued_at = invoice.issued_at or timezone.now()
#     invoice.amount = invoice.bulk_order.total_amount
#     invoice.save(update_fields=["status", "issued_at", "amount"])
#     return invoice


# def mark_invoice_paid(invoice: Invoice) -> Invoice:
#     invoice.status = "paid"
#     invoice.paid_at = timezone.now()
#     invoice.save(update_fields=["status", "paid_at"])
#     return invoice





# # economic/b2b/services/invoice_service.py
# from economic.b2b.models import Invoice

# def mark_invoice_paid(invoice: Invoice):
#     invoice.status = "paid"
#     invoice.save(update_fields=["status"])
