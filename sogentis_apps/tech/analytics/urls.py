# tech/analytics/urls.py
from __future__ import annotations
from django.urls import path
from .views import analytics_index_view

app_name = "analytics"

urlpatterns = [
    path("", analytics_index_view, name="index"),
]
