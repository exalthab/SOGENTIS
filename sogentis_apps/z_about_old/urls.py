# about/urls.py
from django.urls import path
from . import views
from z_about_old.views.about_index import about_index_view


app_name = "about"

urlpatterns = [
    path("", about_index_view, name="about_index"),
    # path("children/", views.children_list, name="children_list"),
    # path("child/<int:pk>/", views.child_detail, name="child_detail"),
    # path("child/<int:pk>/support/", views.child_support_view, name="child_support"),
    # path("mother/<int:pk>/", views.mother_detail, name="mother_detail"),
]

