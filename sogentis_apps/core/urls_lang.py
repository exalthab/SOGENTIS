from django.urls import path
from .views.lang import switch_language, force_language

urlpatterns = [
    path("switch/", switch_language, name="switch_language"),
    path("force/", force_language, name="force_language"),
]
