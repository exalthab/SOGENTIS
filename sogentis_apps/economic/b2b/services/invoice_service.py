# economic/b2b/services/invoice_service.py
from economic.b2b.models import Invoice

def mark_invoice_paid(invoice: Invoice):
    invoice.status = "paid"
    invoice.save(update_fields=["status"])
