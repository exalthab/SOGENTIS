# economic/b2b/views/vendors.py
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render

from economic.ecommerce.models.order_item import OrderItem
from economic.ecommerce.models.product import Product
from ..permissions import is_verified_vendor


@login_required
def vendors_view(request):
    """
    Dashboard vendeur (Marketplace)
    - liste produits vendeur
    - stats ventes via OrderItem
    """
    if not is_verified_vendor(request.user):
        return redirect("b2b:index")

    vendor = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor).order_by("-created_at")

    sales_qs = OrderItem.objects.filter(product__vendor=vendor)

    totals = sales_qs.aggregate(
        items_sold=Coalesce(Sum("quantity"), 0),
        orders_count=Coalesce(Count("order", distinct=True), 0),
        # ✅ CA = sum(unit_price * quantity)
        revenue=Coalesce(Sum(F("unit_price") * F("quantity")), 0),
    )

    context = {"vendor": vendor, "products": products, "totals": totals}
    return render(request, "economic/b2b/vendors/vendor_dashboard.html", context)







# # economic/b2b/views/vendors.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db.models import Sum, Count

# from economic.ecommerce.models.product import Product
# from economic.ecommerce.models.order_item import OrderItem

# from ..permissions import is_verified_vendor


# @login_required
# def vendors_view(request):
#     """
#     Dashboard vendeur (Marketplace)
#     - liste produits vendeur
#     - stats ventes via OrderItem
#     """
#     if not is_verified_vendor(request.user):
#         return redirect("b2b:dashboard")

#     vendor = request.user.vendor_profile

#     products = Product.objects.filter(vendor=vendor).order_by("-created_at")

#     # Stats: ventes (quantités + CA) via OrderItem
#     sales_qs = OrderItem.objects.filter(product__vendor=vendor)
#     totals = sales_qs.aggregate(
#         items_sold=Sum("quantity"),
#         orders_count=Count("order", distinct=True),
#         revenue=Sum("unit_price"),
#     )

#     context = {
#         "vendor": vendor,
#         "products": products,
#         "totals": totals,
#     }
#     return render(request, "b2b/vendor_dashboard.html", context)
