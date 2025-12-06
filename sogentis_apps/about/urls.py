from django.urls import path
from about.views.about_index import about_index_view
from about import views

app_name = "about"

urlpatterns = [
    # path('', about_index_view, name='index'),
    path("", about_index_view, name="about_index"),

]
