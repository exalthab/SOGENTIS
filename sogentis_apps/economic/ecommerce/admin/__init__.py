# ecommerce/admin/__init__.py
# (facultatif, mais propre) permet d’importer le package admin au besoin.
from .cart_admin import CartAdmin
from .order_admin import OrderAdmin
from .product_admin import ProductAdmin
from .vendor_admin import VendorAdmin
from .review_admin import ReviewAdmin
from .category_admin import CategoryAdmin
from .invoice_admin import InvoiceAdmin
from .payment_admin import PaymentTransactionAdmin
from .order_item_admin import OrderItemAdmin
from .wishlist_admin import WishlistAdmin

