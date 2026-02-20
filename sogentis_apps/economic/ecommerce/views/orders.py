# economic/ecommerce/views/orders.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from ..models.order import Order


@login_required
def orders_view(request):
    """
    Alias list.
    URL: path("orders/", orders_view, name="orders")
    """
    return order_list_view(request)


@login_required
def order_list_view(request):
    """
    URL: path("orders/list/", order_list_view, name="order_list")
    """
    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
    )
    return render(request, "economic/ecommerce/orders/order_list.html", {"orders": orders})


@login_required
def order_detail_view(request, uuid):
    """
    URL: path("orders/<uuid:uuid>/", order_detail_view, name="order_detail")
    """
    order = get_object_or_404(Order, uuid=uuid, user=request.user)
    return render(request, "economic/ecommerce/orders/order_detail.html", {"order": order})


@require_POST
@login_required
def order_track_view(request):
    """
    Track simple: l’utilisateur doit être connecté.
    - Si uuid appartient à l’utilisateur (ou staff) -> redirige vers detail.
    """
    uuid = (request.POST.get("uuid") or "").strip()
    if not uuid:
        messages.error(request, _("Veuillez saisir un numéro de commande."))
        return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

    qs = Order.objects.filter(uuid=uuid)
    if not request.user.is_staff:
        qs = qs.filter(user=request.user)

    order = qs.first()
    if not order:
        messages.error(request, _("Commande introuvable ou non autorisée."))
        return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

    return redirect("economic:ecommerce:order_detail", uuid=order.uuid)







# # economic/ecommerce/views/orders.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, render

# from ..models.order import Order


# @login_required
# def orders_view(request):
#     """
#     URL:
#       path("orders/", orders_view, name="orders")
#     """
#     return order_list_view(request)


# @login_required
# def order_list_view(request):
#     """
#     URL:
#       path("orders/list/", order_list_view, name="order_list")
#     """
#     orders = Order.objects.filter(user=request.user).order_by("-created_at")
#     return render(request, "economic/ecommerce/orders/order_list.html", {"orders": orders})


# @login_required
# def order_detail_view(request, uuid):
#     """
#     URL:
#       path("orders/<uuid:uuid>/", order_detail_view, name="order_detail")
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     return render(request, "economic/ecommerce/orders/order_detail.html", {"order": order})

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.utils.translation import gettext as _
# from django.views.decorators.http import require_POST

# @require_POST
# @login_required
# def order_track_view(request):
#     """
#     Track simple: l’utilisateur doit être connecté.
#     - Si uuid appartient à l’utilisateur (ou staff) -> redirige vers detail.
#     """
#     uuid = (request.POST.get("uuid") or "").strip()
#     if not uuid:
#         messages.error(request, _("Veuillez saisir un numéro de commande."))
#         return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

#     qs = Order.objects.filter(uuid=uuid)
#     if not request.user.is_staff:
#         qs = qs.filter(user=request.user)

#     order = qs.first()
#     if not order:
#         messages.error(request, _("Commande introuvable ou non autorisée."))
#         return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

#     return redirect("economic:ecommerce:order_detail", uuid=order.uuid)




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect, render, get_object_or_404

# from ..models.order import Order


# # =====================================================
# # Alias / redirection propre
# # =====================================================
# @login_required
# def orders_view(request):
#     """
#     Alias vers la liste des commandes utilisateur.
#     Évite les doublons (orders.html vs order_list.html).
#     """
#     return redirect("economic:ecommerce:order_list")


# # =====================================================
# # Liste des commandes
# # =====================================================
# @login_required
# def order_list_view(request):
#     orders = (
#         Order.objects
#         .filter(user=request.user)
#         .order_by("-created_at")
#     )
#     return render(
#         request,
#         "economic/ecommerce/orders/order_list.html",
#         {"orders": orders},
#     )


# # =====================================================
# # Détail d'une commande
# # =====================================================
# @login_required
# def order_detail_view(request, uuid):
#     order = get_object_or_404(
#         Order,
#         uuid=uuid,
#         user=request.user,
#     )
#     return render(
#         request,
#         "economic/ecommerce/orders/order_detail.html",
#         {"order": order},
#     )






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
