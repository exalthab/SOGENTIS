# donations/urls.py
from django.urls import path
from . import views

app_name = "donations"

urlpatterns = [
    path("create/", views.create, name="create"),
]
