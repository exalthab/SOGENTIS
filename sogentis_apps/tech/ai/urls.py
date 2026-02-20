# tech/ai/urls.py
from __future__ import annotations
from django.urls import path
from .views import ai_index_view

app_name = "ai"

urlpatterns = [
    path("", ai_index_view, name="index"),
]
