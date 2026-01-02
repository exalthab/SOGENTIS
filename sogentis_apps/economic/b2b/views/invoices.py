# economic/b2b/views/invoices.py
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

from economic.decorators import b2b_admin_required
from economic.b2b.models import Invoice


@b2b_admin_required
def invoices_view(request):
    """
    Liste complète des factures de l'entreprise
    """
    company = request.user.company_user.company
    qs = Invoice.objects.filter(bulk_order__company=company).order_by("-created_at")

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_title": _("Factures"),
        "page_obj": page_obj,
    }
    return render(request, "economic/b2b/invoices/list.html", context)




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
