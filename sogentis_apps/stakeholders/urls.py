from django.urls import path
from .beneficiaries import views as beneficiaries_views

app_name = "stakeholders"

urlpatterns = [
    path("beneficiaries/", beneficiaries_views.beneficiaries_list, name="beneficiaries_list"),
    path("regions/", beneficiaries_views.regions_covered, name="regions_covered"),  # à créer
]