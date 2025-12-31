# /economic/resources/urls.py
from django.urls import path
from .views.index import resources_mod_index_view
from .views.detail import resource_detail_view 

app_name = "resources"


urlpatterns = [
    path("", resources_mod_index_view, name="index"),
    path("<slug:slug>/", resource_detail_view, name="detail"),

]
