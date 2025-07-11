from django.urls import path
from accounts_users.api.views import (
    auth_api,
    password_api,
    registration_api,
    views_api,
)

app_name = "accounts_users_api"

urlpatterns = [
    # Auth
    path("login/", auth_api.LoginAPIView.as_view(), name="api_login"),
    path("logout/", auth_api.LogoutAPIView.as_view(), name="api_logout"),
    
    # Registration
    path("register/", registration_api.RegisterAPIView.as_view(), name="api_register"),
    
    # Password management
    path("password/reset/", password_api.PasswordResetAPIView.as_view(), name="api_password_reset"),
    path("password/change/", password_api.PasswordChangeAPIView.as_view(), name="api_password_change"),
    
    # User info
    path("me/", views_api.UserDetailAPIView.as_view(), name="api_user_detail"),
]
