# economic/services/urls.py
from django.urls import path

from .views import (
    index,
    service_detail,
    request_quote,
    tickets,
    package_detail,
    package_quote,
)

app_name = "services"

urlpatterns = [
    path("", index.services_index_view, name="index"),

    # routes fixes
    path("tickets/", tickets.tickets_view, name="tickets"),

    # packs (✅ ajout)
    path("packs/<slug:slug>/", package_detail.package_detail_view, name="package_detail"),
    path("packs/<slug:slug>/quote/", package_quote.package_quote_view, name="package_quote"),

    # quote service
    path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),

    # catch-all service detail en dernier
    path("<slug:slug>/", service_detail.service_detail_view, name="detail"),
]




# # economic/services/urls.py
# from django.urls import path
# from .views import index, service_detail, request_quote, tickets

# app_name = "services"

# urlpatterns = [
#     path("", index.services_index_view, name="index"),

#     # IMPORTANT : routes fixes avant le slug
#     path("tickets/", tickets.tickets_view, name="tickets"),
#     path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),

#     # Catch-all pour les détails de service en dernier
#     path("<slug:slug>/", service_detail.service_detail_view, name="detail"),
# ]







# # /economic/services/urls.py
# from django.urls import path
# from .views import index, service_detail, request_quote, tickets

# app_name = "services"

# urlpatterns = [
#     path("", index.services_index_view, name="index"),
#     path("<slug:slug>/", service_detail.service_detail_view, name="detail"),
#     path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),
#     path("tickets/", tickets.tickets_view, name="tickets"),
# ]

