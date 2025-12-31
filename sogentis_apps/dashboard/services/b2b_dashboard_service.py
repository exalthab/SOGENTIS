# dashboard/services/b2b_dashboard_service.py
from django.db.models import Sum
from decimal import Decimal

from economic.b2b.models import BulkOrder, Invoice


def get_b2b_dashboard_data(company):
    """
    Retourne les données clés du dashboard B2B pour une entreprise
    """
    orders = (
        BulkOrder.objects
        .filter(company=company)
        .order_by("-created_at")
    )

    invoices = (
        Invoice.objects
        .filter(company=company)
        .order_by("-created_at")
    )

    total_spent = (
        invoices
        .filter(status="paid")
        .aggregate(total=Sum("total_amount"))
        .get("total")
        or Decimal("0.00")
    )

    return {
        "orders_count": orders.count(),
        "invoices_count": invoices.count(),
        "total_spent": total_spent,
        "recent_orders": orders[:5],
        "recent_invoices": invoices[:5],
    }






# # dashboard/services/b2b_dashboard_service.py
# from economic.b2b.models import BulkOrder, Invoice

# def get_b2b_dashboard_data(company):
#     orders = BulkOrder.objects.filter(company=company)
#     invoices = Invoice.objects.filter(company=company)

#     total_spent = sum(inv.total_amount for inv in invoices if inv.status == "paid")

#     return {
#         "orders_count": orders.count(),
#         "invoices_count": invoices.count(),
#         "total_spent": total_spent,
#         "recent_invoices": invoices[:10],
#     }
