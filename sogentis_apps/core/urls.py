from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("contact/", views.contact_view, name="contact"),
    path("politique-confidentialité/", views.privacy_policy, name="privacy_policy"),
    path("conditions-utilisation/", views.cgu, name="cgu"),
    path("politique-cookies/", views.cookies_policy, name="cookies_policy"),
]
