from django.urls import path
from . import views

app_name = "gestion_projets"

urlpatterns = [
    path("services/", views.services_list, name="services"),
    path("services/<slug:slug>/", views.service_detail_view, name="service_detail"),
    # ... autres routes
]
