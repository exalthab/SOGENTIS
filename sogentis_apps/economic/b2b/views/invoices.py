# economic/b2b/views/invoices.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from economic.b2b.models import BulkOrder, Invoice
from economic.b2b.services import company_user_required, create_invoice_for_bulk_order


@login_required
@company_user_required(role="staff")
def invoice_create_for_order_view(request, company_id: int, order_id: int):
    company = request.company
    order = get_object_or_404(BulkOrder, pk=order_id, company=company)

    inv = create_invoice_for_bulk_order(order, issue=True)
    order.status = BulkOrder.Status.INVOICED
    order.save(update_fields=["status", "updated_at"])

    messages.success(request, "Facture créée.")
    return redirect("economic:b2b:invoice_detail", company_id=company.id, invoice_id=inv.id)


@login_required
@company_user_required(role="viewer")
def invoice_detail_view(request, company_id: int, invoice_id: int):
    company = request.company
    invoice = get_object_or_404(Invoice, pk=invoice_id, bulk_order__company=company)
    items = invoice.bulk_order.items.select_related("product").order_by("id")
    return render(
        request,
        "economic/b2b/invoices/invoice_detail.html",
        {"company": company, "invoice": invoice, "items": items},
    )





# # economic/b2b/views/invoices.py
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _

# from economic.decorators import b2b_admin_required
# from economic.b2b.models import Invoice


# @b2b_admin_required
# def invoices_view(request):
#     """
#     Liste complète des factures de l'entreprise
#     """
#     company = request.user.company_user.company
#     qs = Invoice.objects.filter(bulk_order__company=company).order_by("-created_at")

#     paginator = Paginator(qs, 20)
#     page_obj = paginator.get_page(request.GET.get("page"))

#     context = {
#         "page_title": _("Factures"),
#         "page_obj": page_obj,
#     }
#     return render(request, "economic/b2b/invoices/list.html", context)




# # /economic/b2b/views/invoices.py

# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from economic.decorators import b2b_admin_required
# from economic.b2b.models import Invoice


# @b2b_admin_required
# def invoices_view(request):
#     """
#     Page de gestion des factures B2B
#     (liste complète des factures de l'entreprise)
#     """
#     company = request.user.company_user.company

#     invoices = Invoice.objects.filter(
#         bulk_order__company=company
#     ).order_by("-created_at")

#     context = {
#         "page_title": _("Factures"),
#         "invoices": invoices,
#     }

#     return render(
#         request,
#         "b2b/invoices/list.html",
#         context,
#     )







# # economic/b2b/views/invoices.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def invoices_view(request):
#     """
#     Page de gestion des factures
#     """
#     # Replace with actual queryset or logic
#     context = {
#         "invoices": []  # Replace with your real invoices queryset
#     }
#     return render(request, "b2b/invoices.html", context)
