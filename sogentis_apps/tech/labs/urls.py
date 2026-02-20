# tech/labs/urls.py
from __future__ import annotations
from django.urls import path
from .views import labs_index_view

app_name = "labs"

urlpatterns = [
    path("", labs_index_view, name="index"),
]
