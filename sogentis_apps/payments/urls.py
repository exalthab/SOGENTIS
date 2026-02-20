# payments/urls.py
from __future__ import annotations

from django.urls import path

from .views.checkout import checkout_view, success_view, cancel_view
from .views.providers import provider_start_view

app_name = "payments"

urlpatterns = [
    path("checkout/<uuid:uuid>/", checkout_view, name="checkout"),
    path("success/<uuid:uuid>/", success_view, name="success"),
    path("cancel/<uuid:uuid>/", cancel_view, name="cancel"),

    # ✅ un seul endpoint "start" pour provider (Stripe/PayPal/Wave/OM/Visa)
    path("start/<uuid:uuid>/<str:provider>/", provider_start_view, name="provider_start"),
]

