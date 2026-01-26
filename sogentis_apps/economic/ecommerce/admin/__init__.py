# ecommerce/admin/__init__.py
# Charge explicitement tous les modules admin (enregistrements @admin.register)

from . import category_admin  # noqa: F401
from . import vendor_admin  # noqa: F401
from . import product_admin  # noqa: F401
from . import cart_admin  # noqa: F401
from . import cart_item_admin  # noqa: F401
from . import order_admin  # noqa: F401
from . import wishlist_admin  # noqa: F401
from . import wishlist_item_admin  # noqa: F401
from . import review_admin  # noqa: F401
from . import payment_admin  # noqa: F401
from . import product_image_admin  # noqa: F401
from . import product_pricing_admin # noqa: F401
from . import invoice_admin  # noqa: F401
from . import favorite_admin  # noqa: F401
from . import sku_sequence_admin  # noqa: F401
from . import order_item_admin  # noqa: F401






# # ecommerce/admin/__init__.py
# # (facultatif, mais propre) permet d’importer le package admin au besoin.
# from .cart_admin import CartAdmin
# from .order_admin import OrderAdmin
# from .product_admin import ProductAdmin
# from .vendor_admin import VendorAdmin
# from .review_admin import ReviewAdmin
# from .category_admin import CategoryAdmin
# from .invoice_admin import InvoiceAdmin
# from .payment_admin import PaymentTransactionAdmin
# from .order_item_admin import OrderItemAdmin
# from .wishlist_admin import WishlistAdmin

