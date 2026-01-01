# economic/ecommerce/views/vendor/vendor_dashboard.py
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from ...models.order import Order
from ...models.order_item import OrderItem
from ...models.product import Product


@login_required
def vendor_dashboard_view(request):
    """
    URL:
      path("vendor/dashboard/", vendor_dashboard_view, name="vendor_dashboard")
    """
    orders_qs = Order.objects.all()
    items_qs = OrderItem.objects.all()
    products_qs = Product.objects.all()

    total_sales = orders_qs.aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")
    orders_count = orders_qs.count()
    products_count = products_qs.count()

    top_rows = (
        items_qs.values("product_id", "product__name")
        .annotate(total_quantity=Sum("quantity"), total_sales=Sum("line_total"))
        .order_by("-total_quantity")[:10]
    )

    class TopProduct:
        def __init__(self, name, total_quantity, total_sales):
            self.name = name
            self.total_quantity = total_quantity
            self.total_sales = total_sales

    top_products = [
        TopProduct(
            name=row["product__name"],
            total_quantity=row["total_quantity"] or 0,
            total_sales=row["total_sales"] or Decimal("0.00"),
        )
        for row in top_rows
    ]

    recent_orders = orders_qs.order_by("-created_at")[:10]

    return render(
        request,
        "economic/ecommerce/vendor/dashboard.html",
        {
            "stats": {
                "total_sales": total_sales,
                "orders_count": orders_count,
                "products_count": products_count,
            },
            "recent_orders": recent_orders,
            "top_products": top_products,
        },
    )




# # /economic/ecommerce/views/vendor/vendor_dashboard.py
# from django.shortcuts import render
# from django.db.models import Sum
# from economic.decorators import verified_vendor_required
# from economic.ecommerce.models import Product, OrderItem


# @verified_vendor_required
# def vendor_dashboard_view(request):
#     vendor = request.user.vendor

#     products = Product.objects.filter(vendor=vendor)
#     order_items = OrderItem.objects.filter(product__vendor=vendor)

#     stats = {
#         "products_count": products.count(),
#         "orders_count": order_items.values("order").distinct().count(),
#         "total_sales": order_items.aggregate(
#             total=Sum("unit_price")
#         )["total"] or 0,
#     }

#     context = {
#         "vendor": vendor,
#         "products": products[:10],
#         "stats": stats,
#     }

#     return render(
#         request,
#         "economic/ecommerce/vendor/dashboard.html",
#         context,
#     )
