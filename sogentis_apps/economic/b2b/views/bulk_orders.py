# economic/b2b/views/bulk_orders.py
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

from economic.decorators import b2b_required
from economic.b2b.models import BulkOrder


@b2b_required
def bulk_orders_view(request):
    """
    Liste des commandes en gros pour l'entreprise du user connecté
    """
    company = request.user.company_user.company

    qs = BulkOrder.objects.filter(company=company).order_by("-created_at")
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_title": _("Commandes en gros"),
        "page_obj": page_obj,
    }
    return render(request, "economic/b2b/bulk_orders/list.html", context)




# # economic/b2b/views/bulk_orders.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def bulk_orders_view(request):
#     """
#     Page de gestion des commandes en gros
#     """
#     # Example context, replace with your real query logic
#     context = {
#         "orders": []  # Replace with your actual bulk orders queryset
#     }
#     return render(request, "b2b/bulk_orders.html", context)
