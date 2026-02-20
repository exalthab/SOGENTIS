# economic/ecommerce/urls.py
from django.urls import path, include

from .views.index import ecommerce_index_view
from .views.search import ecommerce_search_view
from .views.product_detail import product_detail_view
from .views.favorites import favorite_toggle_view
from .views.favorites_list import favorites_list_view

from .views.cart import (
    cart_view,
    add_to_cart_view,
    update_cart_view,
    remove_from_cart_view,
)

from .views.checkout import checkout_view

from .views.orders import (
    orders_view,
    order_list_view,
    order_detail_view,
)

from .views.invoice import invoice_download_view, proforma_download_view

from .views.wishlist import (
    wishlist_view,
    add_to_wishlist_view,
    remove_from_wishlist_view,
)

from .views.review import add_review_view

from .views.payments import (
    choose_payment_view,
    provider_checkout_view,
    webhook_generic_view,
)

from .views.vendor.vendor_dashboard import vendor_dashboard_view
from .views.order_tracking import order_tracking_view

from .views.switch_mode import switch_mode_view

# ✅ AJOUTS
from .views.quotes import request_quote_view
from .views.likes import like_toggle_view


app_name = "ecommerce"

urlpatterns = [
    # ==========================
    # Catalogue / Home
    # ==========================
    path("", ecommerce_index_view, name="index"),
    path("search/", ecommerce_search_view, name="search"),
    path("categorie/<slug:category_slug>/", ecommerce_index_view, name="category"),

    # Articles (module séparé)
    path("articles/", include("economic.ecommerce.articles.urls")),
    path("favorites/", favorites_list_view, name="favorites_list"),
    path("favorites/toggle/<int:product_id>/", favorite_toggle_view, name="favorite_toggle"),

    # ==========================
    # Produits
    # ==========================
    path("products/<slug:slug>/", product_detail_view, name="product_detail"),

    # ==========================
    # Panier (session)
    # item_id = product_id (par choix : panier session)
    # ==========================
    path("cart/", cart_view, name="cart"),
    path("cart/items/add/<int:product_id>/", add_to_cart_view, name="add_to_cart"),
    path("cart/update/<int:item_id>/", update_cart_view, name="update_cart"),
    path("cart/items/remove/<int:item_id>/", remove_from_cart_view, name="remove_from_cart"),

    # ==========================
    # Checkout
    # ==========================
    path("checkout/", checkout_view, name="checkout"),

    # ==========================
    # Paiements
    # ==========================
    path("payments/choose/<uuid:uuid>/", choose_payment_view, name="choose_payment"),
    path("payments/<str:provider>/<uuid:uuid>/", provider_checkout_view, name="payment_checkout"),
    path("payments/webhook/<str:provider>/", webhook_generic_view, name="payment_webhook"),

    # ==========================
    # Commandes
    # ==========================
    path("orders/", orders_view, name="orders"),
    path("orders/list/", order_list_view, name="order_list"),
    path("orders/<uuid:uuid>/", order_detail_view, name="order_detail"),

    # ==========================
    # Factures
    # ==========================
    path("invoices/<uuid:uuid>/download/", invoice_download_view, name="invoice_download"),
    path("proformas/<uuid:uuid>/download/", proforma_download_view, name="proforma_download"),
    # ==========================
    # Wishlist
    # ==========================
    path("wishlist/", wishlist_view, name="wishlist"),
    path("wishlist/items/add/<int:product_id>/", add_to_wishlist_view, name="wishlist_add"),
    path("wishlist/items/remove/<int:product_id>/", remove_from_wishlist_view, name="wishlist_remove"),

    # ==========================
    # Avis produits
    # ==========================
    path("reviews/add/<int:product_id>/", add_review_view, name="add_review"),

    # ==========================
    # Vendor / Seller
    # ==========================
    path("vendor/dashboard/", vendor_dashboard_view, name="vendor_dashboard"),
    path("orders/track/", order_tracking_view, name="order_track"),

    # ==========================
    # Mode B2C / B2B
    # ==========================
    path("switch-mode/<str:mode>/", switch_mode_view, name="switch_mode"),

    # ✅ NOUVEAUX : pour que les liens template soient actifs
    path("quotes/request/<int:product_id>/", request_quote_view, name="request_quote"),
    path("likes/toggle/<int:product_id>/", like_toggle_view, name="like_toggle"),
]






# # economic/ecommerce/urls.py
# from django.urls import path, include

# from .views.index import ecommerce_index_view
# from .views.product_detail import product_detail_view

# from .views.invoice import invoice_download_view

# from .views.cart import (
#     cart_view,
#     add_to_cart_view,
#     update_cart_view,
#     remove_from_cart_view,
# )

# from .views.checkout import checkout_view

# from .views.orders import (
#     orders_view,
#     order_list_view,
#     order_detail_view,
# )

# from .views.wishlist import (
#     wishlist_view,
#     add_to_wishlist_view,
#     remove_from_wishlist_view,
# )

# from .views.review import add_review_view

# from .views.payments import (
#     provider_checkout_view,
#     webhook_generic_view,
#     choose_payment_view,

# )

# from .views.vendor.vendor_dashboard import vendor_dashboard_view
# from .views.search import ecommerce_search_view
# from .views.switch_mode import switch_mode_view


# app_name = "ecommerce"

# urlpatterns = [

#     # ==========================
#     # Catalogue / Home
#     # ==========================
#     path("", ecommerce_index_view, name="index"),
#     path("search/", ecommerce_search_view, name="search"),
#     path("articles/", include("economic.ecommerce.articles.urls")),
#     path("categorie/<slug:category_slug>/", ecommerce_index_view, name="category"),

#     # ==========================
#     # Produits
#     # ==========================
#     path(
#         "products/<slug:slug>/",
#         product_detail_view,
#         name="product_detail",
#     ),

#     # ==========================
#     # Panier
#     # ==========================
#     path("cart/", cart_view, name="cart"),
#     path(
#         "cart/items/add/<int:product_id>/",
#         add_to_cart_view,
#         name="add_to_cart",
#     ),
#     path(
#         "cart/update/<int:item_id>/",
#         update_cart_view,
#         name="update_cart",
#     ),
#     path(
#         "cart/items/remove/<int:item_id>/",
#         remove_from_cart_view,
#         name="remove_from_cart",
#     ),

#     # ==========================
#     # Checkout
#     # ==========================
#     path(
#         "checkout/",
#         checkout_view,
#         name="checkout",
#     ),

#     # ==========================
#     # Paiements
#     # ==========================
#     path(
#       "payments/choose/<uuid:uuid>/",
#        choose_payment_view,
#        name="choose_payment",
#    ),
#     path(
#         "payments/<str:provider>/<uuid:uuid>/",
#         provider_checkout_view,
#         name="payment_checkout",
#     ),
#     path(
#         "payments/webhook/<str:provider>/",
#         webhook_generic_view,
#         name="payment_webhook",
#     ),

#     # ==========================
#     # Commandes
#     # ==========================
#     path("orders/", orders_view, name="orders"),
#     path("orders/list/", order_list_view, name="order_list"),
#     path(
#         "orders/<uuid:uuid>/",
#         order_detail_view,
#         name="order_detail",
#     ),

#     path(
#         "invoices/<uuid:uuid>/download/",
#         invoice_download_view,
#         name="invoice_download",
#     ),
    
#     # ==========================
#     # Wishlist 
#     # ==========================
#     path("wishlist/", wishlist_view, name="wishlist"),
#     path(
#         "wishlist/items/add/<int:product_id>/",
#         add_to_wishlist_view,
#         name="wishlist_add",
#     ),
#     path(
#         "wishlist/items/remove/<int:product_id>/",
#         remove_from_wishlist_view,
#         name="wishlist_remove",
#     ),

#     # ==========================
#     # Avis produits
#     # ==========================
#     path(
#         "reviews/add/<int:product_id>/",
#         add_review_view,
#         name="add_review",
#     ),

#     # ==========================
#     # Vendor / Seller
#     # ==========================
#     path(
#         "vendor/dashboard/",
#         vendor_dashboard_view,
#         name="vendor_dashboard",
#     ),

#     # ==========================
#     # Mode B2C / B2B
#     # ==========================
#     path(
#         "switch-mode/<str:mode>/",
#         switch_mode_view,
#         name="switch_mode",
#     ),
# ]









# # economic/ecommerce/urls.py
# from django.urls import path, include

# from .views.index import ecommerce_index_view

# from .views.product_detail import product_detail_view

# from .views.cart import (
#     cart_view,
#     add_to_cart_view,
#     remove_from_cart_view,
# )
# from .views.cart import cart_view, update_cart_view, remove_from_cart_view

# from .views.checkout import checkout_view

# from .views.orders import (
#     orders_view,
#     order_list_view,
#     order_detail_view,
# )

# from .views.wishlist import (
#     wishlist_view,
#     add_to_wishlist_view,
#     remove_from_wishlist_view,
# )

# from .views.review import add_review_view
# # from .views.payments import _dummy_checkout

# from .views.vendor.vendor_dashboard import vendor_dashboard_view

# from .views.search import search_view
# from .views.switch_mode import switch_mode_view
# # from economic.ecommerce.articles import views

# app_name = "ecommerce"

# urlpatterns = [

#     # ==========================
#     # Catalogue / Home
#     # ==========================
#     path("", ecommerce_index_view, name="index"),

#     # path("", catalog1_view, name="shop"),
#     path("search/", search_view, name="search"),
#     # path("articles/", views, name="articles"),
#     path("articles/", include("economic.ecommerce.articles.urls")),

#     # ==========================
#     # Produits
#     # ==========================
#     path("products/<slug:slug>/", product_detail_view, name="product_detail"),

#     # ==========================
#     # Panier (POST only côté vues)
#     # ==========================
#     path("cart/", cart_view, name="cart"),
#     path("cart/items/add/<int:product_id>/", add_to_cart_view, name="cart_add"),
#     path("cart/items/remove/<int:item_id>/", remove_from_cart_view, name="cart_remove"),
#     # path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
#     # path("quote/request/", views.request_quote, name="request_quote"),
#     path("cart/update/<int:item_id>/", update_cart_view, name="update_cart"),
#     path("cart/remove/<int:item_id>/", remove_from_cart_view, name="remove_from_cart"),

#     # ==========================
#     # Checkout
#     # ==========================
#     path("checkout/", checkout_view, name="checkout"),

#     # ==========================
#     # Commandes
#     # ==========================
#     path("orders/", orders_view, name="orders"),
#     path("orders/", order_list_view, name="order_list"),
#     path("orders/<uuid:uuid>/", order_detail_view, name="order_detail"),

#     # ==========================
#     # Wishlist
#     # ==========================
#     path("wishlist/", wishlist_view, name="wishlist"),
#     path("wishlist/items/add/<int:product_id>/", add_to_wishlist_view, name="wishlist_add"),
#     path("wishlist/items/remove/<int:product_id>/", remove_from_wishlist_view, name="wishlist_remove"),

#     # ==========================
#     # Avis produits
#     # ==========================
#     path("reviews/add/<int:product_id>/", add_review_view, name="add_review"),

#     # ==========================
#     # Paiements
#     # ==========================
#     # path(
#     #     "payments/<str:provider>/<uuid:uuid>/",
#     #     _dummy_checkout,
#     #     name="payment_checkout",
#     # ),

#     # ==========================
#     # Vendor / Seller
#     # ==========================
#     path("vendor/dashboard/", vendor_dashboard_view, name="vendor_dashboard"),
#         path(
#         "switch-mode/<str:mode>/",
#         switch_mode_view,
#         name="switch_mode",
#     ),
# ]








# # /economic/ecommerce/urls.py
# from django.urls import path
# from .views import (
#     catalog1,
#     product_detail,
#     cart,
#     checkout,
#     orders,
#     wishlist,
#     review,
#     payments,
# )

# app_name = "ecommerce"

# urlpatterns = [
#     path("", catalog1.catalog1_view, name="catalog1"),
#     path("product/<slug:slug>/", product_detail.product_detail_view, name="product_detail"),

#     path("cart/", cart.cart_view, name="cart"),
#     path("cart/add/<int:product_id>/", cart.add_to_cart_view, name="cart_add"),
#     path("cart/remove/<int:item_id>/", cart.remove_from_cart_view, name="cart_remove"),

#     path("checkout/", checkout.checkout_view, name="checkout"),

#     path("orders/", orders.order_list_view, name="order_list"),
#     path("orders/<uuid:uuid>/", orders.order_detail_view, name="order_detail"),

#     path("wishlist/", wishlist.wishlist_view, name="wishlist"),
#     path("wishlist/add/<int:product_id>/", wishlist.add_to_wishlist_view, name="wishlist_add"),
#     path("wishlist/remove/<int:product_id>/", wishlist.remove_from_wishlist_view, name="wishlist_remove"),
#     path("review/add/<int:product_id>/", review.add_review_view, name="add_review"),
#     path("payments/<str:provider>/<uuid:uuid>/", payments._dummy_checkout, name="payment_checkout"),

# ]
