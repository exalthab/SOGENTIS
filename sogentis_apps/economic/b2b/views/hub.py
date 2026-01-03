# # economic/b2b/views/hub.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from ..services.permissions import company_user_required


# @company_user_required
# def b2b_hub_view(request):
#     cu = request.company_user
#     stats = {
#         "orders_total": cu.company.bulk_orders.count(),
#         "orders_submitted": cu.company.bulk_orders.filter(status="submitted").count(),
#         "orders_invoiced": cu.company.bulk_orders.filter(status="invoiced").count(),
#         "invoices_total": getattr(cu.company, "bulk_orders", None),
#     }
#     return render(request, "economic/b2b/hub.html", {"company_user": cu, "stats": stats, "page_title": _("Espace B2B")})
