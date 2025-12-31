# dashboard/urls/user.py
from django.urls import path
from dashboard.views.user.home import user_dashboard_home_view

app_name = "dashboard_user"

urlpatterns = [
    path("", user_dashboard_home_view, name="home"),
]
