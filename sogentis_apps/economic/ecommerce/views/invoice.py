from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import FileResponse

from ..models.invoice import Invoice


@login_required
def invoice_download_view(request, uuid):
    invoice = get_object_or_404(
        Invoice,
        uuid=uuid,
        order__user=request.user,
    )
    return FileResponse(
        invoice.file.open("rb"),
        as_attachment=True,
        filename=invoice.file.name,
    )
