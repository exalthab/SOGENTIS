# dashboard/views/vendor/revenues.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from economic.ecommerce.models import OrderItem

@login_required
def vendor_revenues(request):
    sales = OrderItem.objects.filter(product__vendor=request.user.vendor)
    return render(request, "dashboard/vendor/revenues.html", {"sales": sales})
