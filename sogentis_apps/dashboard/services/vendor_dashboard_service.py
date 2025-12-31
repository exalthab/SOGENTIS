# dashboard/services/vendor_dashboard_service.py

from django.db.models import Sum, F
from economic.ecommerce.models import Product, Order, OrderItem

def get_vendor_dashboard_data(vendor):
    """
    Retourne toutes les données nécessaires pour le dashboard d'un vendeur.
    """
    products = Product.objects.filter(vendor=vendor)
    orders = Order.objects.filter(items__product__vendor=vendor).distinct()

    # Calcul performant du total des ventes directement en base
    total_sales = OrderItem.objects.filter(product__vendor=vendor).aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0

    recent_orders = orders.order_by("-created_at")[:5]

    # 10 dernières ventes
    recent_sales = OrderItem.objects.filter(product__vendor=vendor)\
        .select_related("order", "product")\
        .order_by("-order__created_at")[:10]

    return {
        "vendor": vendor,
        "products_count": products.count(),
        "orders_count": orders.count(),
        "total_sales": total_sales,
        "recent_orders": recent_orders,
        "recent_sales": recent_sales,
    }




# dashboard/services/vendor_dashboard_service.py

# def get_vendor_dashboard_data(vendor):
#     products = Product.objects.filter(vendor=vendor)
#     sales = OrderItem.objects.filter(product__vendor=vendor)

#     total_revenue = sum(item.unit_price * item.quantity for item in sales)

#     return {
#         "products_count": products.count(),
#         "orders_count": sales.values("order").distinct().count(),
#         "total_revenue": total_revenue,
#         "recent_sales": sales.select_related("order")[:10],
#     }
