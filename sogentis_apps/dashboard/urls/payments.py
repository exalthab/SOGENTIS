# dashboard/urls/payments.py
from __future__ import annotations

from django.urls import path

from dashboard.views.payments import index, intents

app_name = "payments"

urlpatterns = [
    path("", index.payments_index_view, name="index"),

    # Payment intents (central)
    path("intents/", intents.payment_intents_list_view, name="intents"),
    path("intents/<uuid:uuid>/", intents.payment_intent_detail_view, name="intent_detail"),
]
