# economic/b2b/urls.py
from django.urls import path

from .views import bulk_orders, index, invoices, vendors
from economic.b2b.views.invoice_dashboard import invoice_dashboard_view
from economic.b2b.views.company_users import (
    company_users_list_view,
    company_user_add_view,
    company_user_edit_view,
)

app_name = "b2b"

urlpatterns = [
    path("", index.b2b_index_view, name="index"),

    path("bulk-orders/", bulk_orders.bulk_orders_view, name="bulk_orders"),

    # ✅ dashboard facturation
    path("invoices/", invoice_dashboard_view, name="invoice_dashboard"),
    # ✅ liste / page complète (si tu en as besoin)
    path("invoices/list/", invoices.invoices_view, name="invoices"),

    path("vendors/", vendors.vendors_view, name="vendors"),

    path("users/", company_users_list_view, name="company_users"),
    path("users/add/", company_user_add_view, name="company_user_add"),
    path("users/<int:pk>/edit/", company_user_edit_view, name="company_user_edit"),
]





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

