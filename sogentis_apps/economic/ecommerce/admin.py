# economic/ecommerce/admin.py
# Django charge ce fichier automatiquement. Il sert de "pont" vers l'admin modulaire.

from __future__ import annotations

from django.contrib import admin

# ✅ Import explicite (évite import * et les surprises)
from .admin.category_admin import CategoryAdmin  # noqa: F401
from .admin.product_admin import ProductAdmin  # noqa: F401
from .admin.vendor_admin import VendorAdmin  # noqa: F401
from .admin.order_admin import OrderAdmin  # noqa: F401
from .admin.order_item_admin import OrderItemAdmin  # noqa: F401
from .admin.cart_admin import CartAdmin, CartItemAdmin  # noqa: F401
from .admin.payment_admin import PaymentTransactionAdmin  # noqa: F401
from .admin.invoice_admin import InvoiceAdmin  # noqa: F401
from .admin.review_admin import ReviewAdmin  # noqa: F401
from .admin.wishlist_admin import WishlistAdmin  # noqa: F401

admin.site.site_header = "SOGENTIS — E-Commerce Admin"
admin.site.site_title = "SOGENTIS Admin"
admin.site.index_title = "Gestion Marketplace & Commandes"




# # economic/ecommerce/admin.py

# from django.contrib import admin

# from .admin.category_admin import *  # noqa
# from .admin.product_admin import *   # noqa
# from .admin.order_admin import *     # noqa
# from .admin.vendor_admin import *    # noqa
# from .admin.review_admin import *    # noqa
# from .admin.cart_admin import *          # noqa
# from .admin.order_item_admin import *    # noqa
# from .admin.payment_admin import *       # noqa
# from .admin.invoice_admin import *       # noqa

# admin.site.site_header = "SOGENTIS — E-Commerce Admin"
# admin.site.site_title = "SOGENTIS Admin"
# admin.site.index_title = "Gestion Marketplace & Commandes"
