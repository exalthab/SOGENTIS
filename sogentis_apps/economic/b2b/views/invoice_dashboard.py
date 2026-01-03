# # economic/b2b/views/invoice_dashboard.py
# from django.db.models import Sum
# from django.shortcuts import render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from economic.decorators import b2b_admin_required
# from economic.b2b.models import Invoice


# @b2b_admin_required
# def invoice_dashboard_view(request):
#     company = request.user.company_user.company
#     today = timezone.now().date()

#     invoices = Invoice.objects.select_related("bulk_order", "bulk_order__company").filter(
#         bulk_order__company=company
#     )

#     stats = {
#         "total_invoices": invoices.count(),
#         "total_amount": invoices.aggregate(total=Sum("amount"))["total"] or 0,
#         "paid_amount": invoices.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0,
#         "pending_amount": invoices.filter(status__in=["draft", "issued"]).aggregate(total=Sum("amount"))["total"] or 0,
#         "overdue_count": invoices.filter(status="issued", due_date__lt=today).count(),
#     }

#     recent_invoices = invoices.order_by("-created_at")[:10]

#     context = {
#         "page_title": _("Facturation"),
#         "company": company,
#         "stats": stats,
#         "invoices": recent_invoices,
#     }

#     return render(request, "economic/b2b/invoices/dashboard.html", context)





# # # /economic/b2b/views/invoice_dashboard.py

# from django.shortcuts import render
# from django.db.models import Sum
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from economic.decorators import b2b_admin_required
# from economic.b2b.models import Invoice


# @b2b_admin_required
# def invoice_dashboard_view(request):
#     company = request.user.company_user.company
#     today = timezone.now().date()

#     invoices = Invoice.objects.filter(
#         bulk_order__company=company
#     )

#     stats = {
#         "total_invoices": invoices.count(),
#         "total_amount": invoices.aggregate(
#             total=Sum("amount")
#         )["total"] or 0,
#         "paid_amount": invoices.filter(
#             status="paid"
#         ).aggregate(total=Sum("amount"))["total"] or 0,
#         "pending_amount": invoices.filter(
#             status__in=["draft", "issued"]
#         ).aggregate(total=Sum("amount"))["total"] or 0,
#         "overdue_count": invoices.filter(
#             status="issued",
#             due_date__lt=today,
#         ).count(),
#     }

#     recent_invoices = invoices.order_by("-created_at")[:10]

#     context = {
#         "page_title": _("Facturation"),
#         "stats": stats,
#         "invoices": recent_invoices,
#     }

#     return render(
#         request,
#         "b2b/invoices/dashboard.html",
#         context,
#     )
