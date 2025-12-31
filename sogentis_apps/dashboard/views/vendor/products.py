from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from dashboard.permissions import is_vendor

from economic.ecommerce.models import Product
from dashboard.forms.vendor.product_form import VendorProductForm


@login_required
def vendor_products_list_view(request):
    if not is_vendor(request.user):
        return render(request, "dashboard/errors/not_authorized.html", status=403)

    products = Product.objects.filter(vendor=request.user.vendor)

    return render(request, "dashboard/vendor/products_list.html", {
        "products": products,
    })


@login_required
def vendor_product_create_view(request):
    if not is_vendor(request.user):
        return render(request, "dashboard/errors/not_authorized.html", status=403)

    form = VendorProductForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        product = form.save(commit=False)
        product.vendor = request.user.vendor
        product.save()
        form.save_m2m()
        return redirect("dashboard:vendor:products")

    return render(request, "dashboard/vendor/product_form.html", {
        "form": form,
        "title": "Ajouter un produit",
    })


@login_required
def vendor_product_update_view(request, pk):
    if not is_vendor(request.user):
        return render(request, "dashboard/errors/not_authorized.html", status=403)

    product = get_object_or_404(
        Product,
        pk=pk,
        vendor=request.user.vendor,
    )

    form = VendorProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
    )

    if form.is_valid():
        form.save()
        return redirect("dashboard:vendor:products")

    return render(request, "dashboard/vendor/product_form.html", {
        "form": form,
        "title": "Modifier le produit",
    })





# # dashboard/views/vendor/products.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from economic.ecommerce.models import Product

# @login_required
# def vendor_products(request):
#     products = Product.objects.filter(vendor=request.user.vendor)
#     return render(request, "dashboard/vendor/products.html", {"products": products})
