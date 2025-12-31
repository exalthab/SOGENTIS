from django.urls import path
from accounts_users.web.views.registration_choice import registration_choice_view

app_name = "accounts_users_registration"

urlpatterns = [
    path("registration/", registration_choice_view, name="registration_choice"),
]
