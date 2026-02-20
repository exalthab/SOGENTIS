# economic/b2b/urls.py
from django.urls import path

from .views.home import b2b_home_view
from .views.companies import company_list_view, company_create_view, company_detail_view
from .views.bulk_orders import (
    bulk_order_list_view,
    bulk_order_create_view,
    bulk_order_detail_view,
    bulk_order_add_item_view,
    bulk_order_submit_view,
)
from .views.invoices import (
    invoice_list_view,
    invoice_detail_view,
    invoice_create_for_order_view,
)
from .views.rfqs import rfq_list_view, rfq_create_view
from .views.offers import offer_create_view

app_name = "b2b"

urlpatterns = [
    path("", b2b_home_view, name="index"),

    path("companies/", company_list_view, name="company_list"),
    path("companies/new/", company_create_view, name="company_create"),
    path("companies/<int:company_id>/", company_detail_view, name="company_detail"),

    path("companies/<int:company_id>/orders/", bulk_order_list_view, name="bulk_order_list"),
    path("companies/<int:company_id>/orders/new/", bulk_order_create_view, name="bulk_order_create"),
    path("companies/<int:company_id>/orders/<int:order_id>/", bulk_order_detail_view, name="bulk_order_detail"),
    path("companies/<int:company_id>/orders/<int:order_id>/add-item/", bulk_order_add_item_view, name="bulk_order_add_item"),
    path("companies/<int:company_id>/orders/<int:order_id>/submit/", bulk_order_submit_view, name="bulk_order_submit"),

    path("companies/<int:company_id>/invoices/", invoice_list_view, name="invoice_list"),
    path("companies/<int:company_id>/orders/<int:order_id>/invoice/create/", invoice_create_for_order_view, name="invoice_create_for_order"),
    path("companies/<int:company_id>/invoices/<int:invoice_id>/", invoice_detail_view, name="invoice_detail"),

    path("companies/<int:company_id>/rfqs/", rfq_list_view, name="rfq_list"),
    path("companies/<int:company_id>/rfqs/new/", rfq_create_view, name="rfq_create"),

    path("rfqs/<int:rfq_id>/offer/new/", offer_create_view, name="offer_create"),
]






# # economic/b2b/urls.py
# from django.urls import path

# from .views.home import b2b_home_view
# from .views.companies import company_list_view, company_create_view, company_detail_view
# from .views.bulk_orders import (
#     bulk_order_list_view,
#     bulk_order_create_view,
#     bulk_order_detail_view,
#     bulk_order_add_item_view,
#     bulk_order_submit_view,
# )
# from .views.invoices import (
#     invoice_list_view,
#     invoice_detail_view,
#     invoice_create_for_order_view,
# )

# from .views.rfqs import rfq_list_view, rfq_create_view
# from .views.offers import offer_create_view

# app_name = "b2b"

# urlpatterns = [
#     path("", b2b_home_view, name="index"),  # ✅ IMPORTANT

#     path("companies/", company_list_view, name="company_list"),
#     path("companies/new/", company_create_view, name="company_create"),
#     path("companies/<int:company_id>/", company_detail_view, name="company_detail"),

#     path("companies/<int:company_id>/orders/", bulk_order_list_view, name="bulk_order_list"),
#     path("companies/<int:company_id>/orders/new/", bulk_order_create_view, name="bulk_order_create"),
#     path("companies/<int:company_id>/orders/<int:order_id>/", bulk_order_detail_view, name="bulk_order_detail"),
#     path("companies/<int:company_id>/orders/<int:order_id>/add-item/", bulk_order_add_item_view, name="bulk_order_add_item"),
#     path("companies/<int:company_id>/orders/<int:order_id>/submit/", bulk_order_submit_view, name="bulk_order_submit"),

#     path("companies/<int:company_id>/orders/<int:order_id>/invoice/create/", invoice_create_for_order_view, name="invoice_create_for_order"),
#     path("companies/<int:company_id>/invoices/<int:invoice_id>/", invoice_detail_view, name="invoice_detail"),

#     path("companies/<int:company_id>/rfqs/", rfq_list_view, name="rfq_list"),
#     path("companies/<int:company_id>/rfqs/new/", rfq_create_view, name="rfq_create"),

#     path("rfqs/<int:rfq_id>/offer/new/", offer_create_view, name="offer_create"),
#     path("companies/<int:company_id>/invoices/", invoice_list_view, name="invoice_list"),

# ]





# # economic/b2b/urls.py
# from django.urls import path

# from .views import bulk_orders, index, invoices, vendors
# from economic.b2b.views.invoice_dashboard import invoice_dashboard_view
# from economic.b2b.views.company_users import (
#     company_users_list_view,
#     company_user_add_view,
#     company_user_edit_view,
# )

# app_name = "b2b"

# urlpatterns = [
#     path("", index.b2b_index_view, name="index"),

#     path("bulk-orders/", bulk_orders.bulk_orders_view, name="bulk_orders"),

#     # ✅ dashboard facturation
#     path("invoices/", invoice_dashboard_view, name="invoice_dashboard"),
#     # ✅ liste / page complète (si tu en as besoin)
#     path("invoices/list/", invoices.invoices_view, name="invoices"),

#     path("vendors/", vendors.vendors_view, name="vendors"),

#     path("users/", company_users_list_view, name="company_users"),
#     path("users/add/", company_user_add_view, name="company_user_add"),
#     path("users/<int:pk>/edit/", company_user_edit_view, name="company_user_edit"),
# ]





# # /economic/b2b/urls.py
# from django.urls import path
# from .views import bulk_orders, index, invoices, vendors
# from economic.b2b.views.invoice_dashboard import (
#     invoice_dashboard_view,
# )
# from economic.b2b.views.company_users import (
#     company_users_list_view,
#     company_user_add_view,
#     company_user_edit_view,
# )

# app_name = "b2b"

# urlpatterns = [
#     path("", index.b2b_index_view, name="index"),
#     path("bulk-orders/", bulk_orders.bulk_orders_view, name="bulk_orders"),
#     path("invoices/", invoices.invoices_view, name="invoices"),
#     path("invoices/", invoice_dashboard_view, name="invoice_dashboard"),
#     path("vendors/", vendors.vendors_view, name="vendors"),
#     path("users/", company_users_list_view, name="company_users"),
#     path("users/add/", company_user_add_view, name="company_user_add"),
#     path("users/<int:pk>/edit/", company_user_edit_view, name="company_user_edit"),
# ]

