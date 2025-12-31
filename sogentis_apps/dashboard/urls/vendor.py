# dashboard/urls/vendor.py
# =====================================================
# URLs pour l’espace Vendeur (Marketplace)
# =====================================================

from django.urls import path
from dashboard.views.vendor.home import vendor_dashboard_home_view
from dashboard.views.vendor.products import (
    vendor_products_list_view,
    vendor_product_create_view,
    vendor_product_update_view,
)

app_name = "dashboard_vendor"

urlpatterns = [
    # Dashboard principal vendeur
    path("", vendor_dashboard_home_view, name="home"),

    # Gestion des produits
    path("products/", vendor_products_list_view, name="products"),
    path("products/add/", vendor_product_create_view, name="product_add"),
    path("products/<int:pk>/edit/", vendor_product_update_view, name="product_edit"),
]





# # dashboard/urls/vendor.py
# from django.urls import path
# from dashboard.views.vendor.index import vendor_dashboard_view
# from dashboard.views.vendor.products import (
#     vendor_products_list_view,
#     vendor_product_create_view,
#     vendor_product_update_view,
# )


# urlpatterns = [
#     path("", vendor_dashboard_view, name="index"),
#     path("products/", vendor_products_list_view, name="products"),
#     path("products/add/", vendor_product_create_view, name="product_add"),
#     path("products/<int:pk>/edit/", vendor_product_update_view, name="product_edit"),
# ]
