from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from ..models.order import Order


# =====================================================
# Alias / redirection propre
# =====================================================
@login_required
def orders_view(request):
    """
    Alias vers la liste des commandes utilisateur.
    Évite les doublons (orders.html vs order_list.html).
    """
    return redirect("economic:ecommerce:order_list")


# =====================================================
# Liste des commandes
# =====================================================
@login_required
def order_list_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )
    return render(
        request,
        "economic/ecommerce/orders/order_list.html",
        {"orders": orders},
    )


# =====================================================
# Détail d'une commande
# =====================================================
@login_required
def order_detail_view(request, uuid):
    order = get_object_or_404(
        Order,
        uuid=uuid,
        user=request.user,
    )
    return render(
        request,
        "economic/ecommerce/orders/order_detail.html",
        {"order": order},
    )






# # economic/ecommerce/views/orders.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect, render, get_object_or_404
# from economic.ecommerce.models.order import Order


# def orders_view(request):
#     return render(request, "economic/ecommerce/orders.html")
#     # return redirect("economic:ecommerce:order_list")

# @login_required
# def order_list_view(request):
#     orders = Order.objects.filter(user=request.user).order_by("-created_at")
#     return render(request, "ecommerce/orders/order_list.html", {"orders": orders})

# @login_required
# def order_detail_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     return render(request, "ecommerce/orders/order_detail.html", {"order": order})
