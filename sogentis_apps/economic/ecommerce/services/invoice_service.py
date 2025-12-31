from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from weasyprint import HTML

from ..models.invoice import Invoice


def generate_invoice_pdf(order):
    invoice, created = Invoice.objects.get_or_create(order=order)

    html = render_to_string(
        "economic/ecommerce/invoices/invoice.html",
        {
            "order": order,
            "invoice": invoice,
        },
    )

    pdf = HTML(
        string=html,
        base_url=settings.STATIC_ROOT  # 🔑 pour images
    ).write_pdf()

    invoice.file.save(
        f"invoice-{invoice.uuid}.pdf",
        ContentFile(pdf),
        save=True,
    )

    return invoice
