# dashboard/views/vendor/home.py
from __future__ import annotations

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.access import require_vendor_approved
from dashboard.views.utils import StatCard, breadcrumb


def _safe_field_names(Model) -> set[str]:
    try:
        return {f.name for f in Model._meta.get_fields()}
    except Exception:
        return set()


@require_vendor_approved
def vendor_dashboard_home_view(request):
    cards = []
    products = []
    orders = []

    # produits vendeur (best-effort)
    try:
        from economic.ecommerce.models.product import Product  # type: ignore
        fields = _safe_field_names(Product)

        qs = Product.objects.all()

        # tentatives de liaison vendeur -> user
        if "vendor" in fields:
            try:
                qs = qs.filter(vendor=request.user)
            except Exception:
                qs = qs.filter(vendor__user=request.user)
        elif "seller" in fields:
            qs = qs.filter(seller=request.user)
        elif "owner" in fields:
            qs = qs.filter(owner=request.user)

        products = list(qs.order_by("-id")[:8])
        cards.append(StatCard(label=_("Produits"), value=qs.count(), icon="📦"))
    except Exception:
        products = []

    # commandes vendeur (best-effort)
    try:
        from economic.ecommerce.models.order import Order  # type: ignore
        qs = Order.objects.all()

        # cas courant: items__product__vendor
        try:
            qs = qs.filter(items__product__vendor=request.user).distinct()
        except Exception:
            try:
                qs = qs.filter(items__product__vendor__user=request.user).distinct()
            except Exception:
                # fallback: si Order a un champ vendor/seller
                fields = _safe_field_names(Order)
                if "vendor" in fields:
                    qs = qs.filter(vendor=request.user)
                elif "seller" in fields:
                    qs = qs.filter(seller=request.user)

        order_field = "created_at" if "created_at" in _safe_field_names(Order) else "id"
        orders = list(qs.order_by(f"-{order_field}")[:8])
        cards.append(StatCard(label=_("Commandes"), value=len(orders), icon="🧾"))
    except Exception:
        orders = []

    return render(request, "dashboard/vendor/home.html", {
        "page_title": _("Espace vendeur"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Vendeur"), None)),
        "cards": [c.__dict__ for c in cards],
        "products": products,
        "orders": orders,
    })






# # dashboard/views/vendor/home.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import StatCard, breadcrumb
# from dashboard.access import require_vendor_approved


# @require_vendor_approved
# def vendor_dashboard_home_view(request):
#     cards = []
#     products = []
#     orders = []

#     # produits vendeur (si modèle dispo)
#     try:
#         from economic.ecommerce.models.product import Product
#         products = Product.objects.filter(vendor=request.user).order_by("-id")[:8]
#         cards.append(StatCard(label=_("Produits"), value=Product.objects.filter(vendor=request.user).count(), icon="📦"))
#     except Exception:
#         products = []

#     # commandes vendeur (si modèle dispo)
#     try:
#         from economic.ecommerce.models.order import Order
#         orders = Order.objects.filter(items__product__vendor=request.user).distinct().order_by("-created_at")[:8]
#         cards.append(StatCard(label=_("Commandes"), value=len(orders), icon="🧾"))
#     except Exception:
#         orders = []

#     return render(request, "dashboard/vendor/home.html", {
#         "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Vendeur"), None)),
#         "cards": [c.__dict__ for c in cards],
#         "products": products,
#         "orders": orders,
#     })




# # dashboard/views/vendor/home.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_vendor
# from dashboard.services.vendor_dashboard_service import get_vendor_dashboard_data


# @login_required
# @user_passes_test(is_vendor)
# def vendor_dashboard_home_view(request):
#     vendor = request.user.vendor

#     context = {
#         "page_title": _("Espace vendeur"),
#         # "section_menu": "core/partials/_menu_dashboard.html",
#         "dashboard_menu": "dashboard/vendor/_menu.html",

#         **get_vendor_dashboard_data(vendor),
#     }

#     return render(request, "dashboard/vendor/home.html", context)




# # dashboard/views/vendor/home.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_vendor
# from dashboard.services.vendor_dashboard_service import get_vendor_dashboard_data

# @login_required
# def vendor_dashboard_home_view(request):
#     if not is_vendor(request.user):
#         return render(request, "dashboard/errors/not_authorized.html", status=403)

#     vendor = request.user.vendor
#     context = get_vendor_dashboard_data(vendor)

#     return render(request, "dashboard/vendor/home.html", context)




# # dashboard/views/vendor/home.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from dashboard.permissions import is_vendor
# from dashboard.services.vendor_dashboard_service import get_vendor_dashboard_data

# @login_required
# def vendor_dashboard_view(request):
#     if not is_vendor(request.user):
#         return render(request, "dashboard/errors/403.html", status=403)

#     vendor = request.user.vendor
#     context = get_vendor_dashboard_data(vendor)

#     return render(request, "dashboard/vendor/home.html", context)
