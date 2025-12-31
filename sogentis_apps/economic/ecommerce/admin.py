# economic/ecommerce/admin.py
# Django charge ce fichier automatiquement. Il sert de "pont" vers l'admin modulaire.

from django.contrib import admin

from .admin.category_admin import *  # noqa
from .admin.product_admin import *   # noqa
from .admin.order_admin import *     # noqa
from .admin.vendor_admin import *    # noqa
from .admin.review_admin import *    # noqa
from .admin.cart_admin import *          # noqa
from .admin.order_item_admin import *    # noqa
from .admin.payment_admin import *       # noqa
from .admin.invoice_admin import *       # noqa

admin.site.site_header = "SOGENTIS — E-Commerce Admin"
admin.site.site_title = "SOGENTIS Admin"
admin.site.index_title = "Gestion Marketplace & Commandes"

