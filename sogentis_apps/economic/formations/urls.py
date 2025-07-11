from django.urls import path
from . import views

app_name = "formations"

urlpatterns = [
    path('', views.formations_list, name='formations_list'),
    path("formations/<slug:slug>/", views.formation_details_view, name="formation_details"),
    # ... autres routes
]
