# dashboard/views/orders.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import breadcrumb


@login_required
def orders_view(request):
    orders = []
    try:
        from economic.ecommerce.models.order import Order  # ajuste si différent
        orders = Order.objects.filter(user=request.user).order_by("-created_at")[:50]
    except Exception:
        orders = []

    return render(request, "dashboard/user/orders_list.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Commandes"), None)),
        "orders": orders,
    })





# # dashboard/views/orders.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator

# @login_required
# def orders_view(request):
#     from economic.ecommerce.models import Order

#     orders_qs = (
#         Order.objects
#         .filter(user=request.user)
#         .order_by("-created_at")
#     )

#     paginator = Paginator(orders_qs, 10)
#     orders_page = paginator.get_page(request.GET.get("page"))

#     return render(request, "dashboard/orders.html", {"orders": orders_page})






# # dashboard/views/orders.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _


# @login_required
# def orders_view(request):
#     from economic.ecommerce.models import Order  # adapter si différent
#     user_email = request.user.email  # identification du client

#     # Récupération des commandes correspondant à l'email de l'utilisateur
#     orders_qs = Order.objects.filter(email=user_email).order_by("-created_at")

#     # Pagination
#     paginator = Paginator(orders_qs, 10)
#     page_number = request.GET.get("page")
#     orders_page = paginator.get_page(page_number)

#     context = {
#         "orders": orders_page,
#     }

#     return render(request, "dashboard/orders.html", context)





# # dashboard/views/orders.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def orders_view(request):

#     orders = [
#         {"id": 1, "client": "Alice", "status": "En cours", "amount": 25000},
#         {"id": 2, "client": "Moussa", "status": "Livré", "amount": 45000},
#     ]

#     return render(request, "dashboard/orders.html", {"orders": orders})
