# economic/services/urls.py
from django.urls import path
from .views import index, service_detail, request_quote, tickets

app_name = "services"

urlpatterns = [
    path("", index.services_index_view, name="index"),

    # IMPORTANT : routes fixes avant le slug
    path("tickets/", tickets.tickets_view, name="tickets"),
    path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),

    # Catch-all pour les détails de service en dernier
    path("<slug:slug>/", service_detail.service_detail_view, name="detail"),
]







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

