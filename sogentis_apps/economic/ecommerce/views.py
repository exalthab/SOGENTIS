# economic/ecommerce/views.py (produits)

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from economic.ecommerce.models import Product, Category, Order, OrderItem
from django.contrib import messages
# from economic.orders.models import Order  # À activer si tu as le modèle de commande

def ecommerce(request):
    return render(request, "economic/econ_index.html")


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if product.stock is not None and product.stock == 0:
        return redirect('ecommerce:product_detail', slug=product.slug)

    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart

    return redirect('ecommerce:cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys(), is_active=True)
    
    cart_items = []
    total = 0

    for p in products:
        qty = cart.get(str(p.id), 0)
        if p.stock is not None and p.stock > 0:
            qty = min(qty, p.stock)
        else:
            qty = 0
        cart_items.append({
            'product': p,
            'qty': qty,
            'subtotal': p.price * qty
        })
        total += p.price * qty

    return render(request, 'economic/cart_detail.html', {
        'cart_items': cart_items,
        'total': total
    })


def products_list(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'economic/products_list.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    similaires = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk)[:4]

    return render(request, "economic/product_detail.html", {
        "product": product,
        "similaires": similaires,
    })


def buynow_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if product.stock is not None and product.stock == 0:
        return redirect('ecommerce:product_detail', slug=product.slug)

    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart

    return redirect('ecommerce:cart_detail')

def checkout_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys(), is_active=True)
    cart_items = []
    total = 0
    for p in products:
        qty = min(cart.get(str(p.id), 0), p.stock)
        cart_items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
        total += p.price * qty

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        if not full_name or not email:
            messages.error(request, "Nom et email obligatoires.")
        elif not cart_items:
            messages.error(request, "Votre panier est vide.")
        else:
            # Création commande
            order = Order.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                total=total
            )
            for item in cart_items:
                # Décrémente le stock
                prod = item['product']
                qty = item['qty']
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    price=prod.price
                )
                prod.stock = max(0, prod.stock - qty)
                prod.save()
            # Vide panier
            request.session['cart'] = {}
            return redirect(reverse('ecommerce:order_confirmation', args=[order.tracking_code]))
    return render(request, "economic/checkout.html", {
        "cart_items": cart_items,
        "total": total,
    })

def order_confirmation(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return render(request, "economic/order_confirmation.html", {"order": order})

def track_order_view(request):
    code = request.GET.get('code')
    order = None
    if code:
        order = Order.objects.filter(tracking_code__iexact=code.strip()).first()
    return render(request, "economic/track_order.html", {"order": order, "code": code})