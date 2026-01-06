#core/urls.py
from django.urls import path
from core.views import views


app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("hub/", views.home_view, name="hub"),   # ✅ page hub toujours accessible
    path("contact/", views.contact_view, name="contact"),
    path("politique-confidentialité/", views.privacy_policy, name="privacy_policy"),
    path("conditions-utilisation/", views.cgu, name="cgu"),
    path("politique-cookies/", views.cookies_policy, name="cookies_policy"),

]
