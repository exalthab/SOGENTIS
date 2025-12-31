from django.shortcuts import render
from ecommerce.models import Product

def ecommerce_home_view(request):
    featured = Product.objects.filter(is_new=True)[:8]
    return render(request, "economic/shop.html", {
        "featured_products": featured,
    })
