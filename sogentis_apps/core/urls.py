#core/urls.py
from django.urls import path
from core.views import views
from core.views.contact import contact_verify_sent_view, contact_verify_view
from .views.lang import switch_language, force_language



app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("hub/", views.home_view, name="hub"),   # ✅ page hub toujours accessible
    path("contact/", views.contact_view, name="contact"),
    path("contact/sent/", contact_verify_sent_view, name="contact_verify_sent"),
    path("contact/verify/<uuid:token>/", contact_verify_view, name="contact_verify"),
    path("politique-confidentialité/", views.privacy_policy, name="privacy_policy"),
    path("conditions-utilisation/", views.cgu, name="cgu"),
    path("politique-cookies/", views.cookies_policy, name="cookies_policy"),
    # ✅ Langue
    path("switch/", switch_language, name="switch_language"),
    path("force/", force_language, name="force_language"),
]
