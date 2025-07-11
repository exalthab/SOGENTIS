from django.urls import path
from . import views

app_name = "econ"

urlpatterns = [
    # Accueil pôle économique
    path("", views.econ_index, name="index"),

    # Catalogue produits, détails produits, filtrage, achat direct, ajout panier
    # path("products/", views.products_list, name="products"),
    # path("products/<slug:slug>/", views.product_detail_view, name="product_detail"),
    # path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    # path("buynow/<int:product_id>/", views.buynow_view, name="buynow"),

    # Panier
    # path("cart/", views.cart_detail, name="cart_detail"),

    # Services/formations
    # path("services/", views.services_list, name="services"),

    # Suivi de commande
    # path("track-order/", views.track_order_view, name="track_order"),
]
