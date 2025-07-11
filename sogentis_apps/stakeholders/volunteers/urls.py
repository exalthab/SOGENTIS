from django.urls import path
from . import views

app_name = "volunteers"

urlpatterns = [
    path("devenir-volontaire/", views.become_volunteer, name="become_volunteer"),
    path("merci/", views.thanks, name="thanks"),
]
