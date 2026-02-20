# tech/integrations/urls.py
from __future__ import annotations
from django.urls import path
from .views import integrations_index_view

app_name = "integrations"

urlpatterns = [
    path("", integrations_index_view, name="index"),
]
