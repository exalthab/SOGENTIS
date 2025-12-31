# dashboard/views/vendor/orders.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from economic.ecommerce.models import OrderItem

@login_required
def vendor_orders(request):
    orders = OrderItem.objects.filter(product__vendor=request.user.vendor)
    return render(request, "dashboard/vendor/orders.html", {"orders": orders})
