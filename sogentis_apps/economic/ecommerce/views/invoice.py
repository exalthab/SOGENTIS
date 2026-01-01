# economic/ecommerce/views/invoice.py
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from ..models.order import Order

try:
    from xhtml2pdf import pisa
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


@login_required
def invoice_download_view(request, uuid):
    """
    URL:
      path("invoices/<uuid:uuid>/download/", invoice_download_view, name="invoice_download")
    """
    order = get_object_or_404(Order, uuid=uuid, user=request.user)
    context = {"order": order}

    if not HAS_PDF:
        html = render(request, "economic/ecommerce/invoices/invoice.html", context).content
        resp = HttpResponse(html, content_type="text/html; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="invoice-{order.uuid}.html"'
        return resp

    html_str = render(request, "economic/ecommerce/invoices/invoice.html", context).content.decode("utf-8")
    result = BytesIO()
    pisa.CreatePDF(html_str, dest=result)

    resp = HttpResponse(result.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="invoice-{order.uuid}.pdf"'
    return resp






# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404
# from django.http import FileResponse

# from ..models.invoice import Invoice


# @login_required
# def invoice_download_view(request, uuid):
#     invoice = get_object_or_404(
#         Invoice,
#         uuid=uuid,
#         order__user=request.user,
#     )
#     return FileResponse(
#         invoice.file.open("rb"),
#         as_attachment=True,
#         filename=invoice.file.name,
#     )
