# #economic/views.py

from django.shortcuts import render, redirect, get_object_or_404
from economic.ecommerce.models import Product, Category

def econ_index(request):
    return render(request, "economic/econ_index.html")

def economic_home(request):
    products = Product.objects.filter(is_active=True)[:6]
    return render(request, 'economic/economic_home.html', {'products': products})

# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('econ:cart_detail')

# def cart_detail(request):
#     cart = request.session.get('cart', {})
#     products = Product.objects.filter(id__in=cart.keys())
#     cart_items = []
#     total = 0
#     for p in products:
#         qty = cart.get(str(p.id), 0)
#         cart_items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
#         total += p.price * qty
#     return render(request, 'economic/cart_detail.html', {'cart_items': cart_items, 'total': total})

# def products_list(request):
#     category_slug = request.GET.get('category')
#     categories = Category.objects.all()
#     products = Product.objects.filter(is_active=True)
#     if category_slug:
#         products = products.filter(category__slug=category_slug)
#     context = {
#         'products': products,
#         'categories': categories,
#     }
#     return render(request, 'economic/products_list.html', context)


# def product_detail_view(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     return render(request, "economic/product_detail.html", {"product": product})

# def buynow_view(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     # Exemple simple : rediriger vers le panier avec ajout
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('econ:cart_detail')

# def track_order_view(request):
#     code = request.GET.get('code')
#     order = None
#     if code:
#         # order = Order.objects.filter(tracking_code=code).first()
#         pass
#     return render(request, "economic/track_order.html", {"order": order, "code": code})
