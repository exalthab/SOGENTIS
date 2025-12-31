# /economic/ecommerce/views/vendor/vendor_dashboard.py
from django.shortcuts import render
from django.db.models import Sum
from economic.decorators import verified_vendor_required
from economic.ecommerce.models import Product, OrderItem


@verified_vendor_required
def vendor_dashboard_view(request):
    vendor = request.user.vendor

    products = Product.objects.filter(vendor=vendor)
    order_items = OrderItem.objects.filter(product__vendor=vendor)

    stats = {
        "products_count": products.count(),
        "orders_count": order_items.values("order").distinct().count(),
        "total_sales": order_items.aggregate(
            total=Sum("unit_price")
        )["total"] or 0,
    }

    context = {
        "vendor": vendor,
        "products": products[:10],
        "stats": stats,
    }

    return render(
        request,
        "economic/ecommerce/vendor/dashboard.html",
        context,
    )
