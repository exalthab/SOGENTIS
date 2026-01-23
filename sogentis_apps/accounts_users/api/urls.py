# accounts_users/api/urls.py
from django.urls import path

from accounts_users.api.views.auth_api import LoginAPIView, LogoutAPIView
from accounts_users.api.views.password_api import PasswordResetAPIView, PasswordChangeAPIView
from accounts_users.api.views.views_api import UserDetailAPIView

from accounts_users.api.views.registration_api import (
    RegistrationMetaAPIView,
    SocialRegistrationAPIView,
    EconomicRegistrationAPIView,
    ResendActivationAPIView,
    ActivateAccountAPIView,
)

app_name = "api"

urlpatterns = [
    # =========================
    # Auth
    # =========================
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),

    # =========================
    # Registration (NEW STRUCT)
    # =========================
    # Meta (tracks disponibles: client/vendor/b2b)
    path("registration/meta/", RegistrationMetaAPIView.as_view(), name="registration_meta"),

    # Social (multipart: docs)
    path("registration/social/", SocialRegistrationAPIView.as_view(), name="registration_social"),

    # Economic (multipart: track=client|vendor|b2b + pièces jointes si besoin)
    path("registration/economic/", EconomicRegistrationAPIView.as_view(), name="registration_economic"),

    # Activation
    path("registration/resend-activation/", ResendActivationAPIView.as_view(), name="resend_activation"),
    path("registration/activate/<str:uidb64>/<str:token>/", ActivateAccountAPIView.as_view(), name="activate"),

    # -------------------------
    # Backward-compat aliases
    # -------------------------
    # Si ton front appelait déjà /api/register/ => on le mappe sur economic
    path("register/", EconomicRegistrationAPIView.as_view(), name="register"),

    # =========================
    # Password
    # =========================
    path("password/reset/", PasswordResetAPIView.as_view(), name="password_reset"),
    path("password/change/", PasswordChangeAPIView.as_view(), name="password_change"),

    # =========================
    # User
    # =========================
    path("me/", UserDetailAPIView.as_view(), name="me"),
]







# #accounts_users/api/urls.py
# from django.urls import path
# from accounts_users.api.views import (
#     auth_api,
#     password_api,
#     registration_api,
#     views_api,
# )

# app_name = "accounts_users_api"

# urlpatterns = [
#     # Auth
#     path("login/", auth_api.LoginAPIView.as_view(), name="api_login"),
#     path("logout/", auth_api.LogoutAPIView.as_view(), name="api_logout"),
    
#     # Registration
#     path("register/", registration_api.RegisterAPIView.as_view(), name="api_register"),
    
#     # Password management
#     path("password/reset/", password_api.PasswordResetAPIView.as_view(), name="api_password_reset"),
#     path("password/change/", password_api.PasswordChangeAPIView.as_view(), name="api_password_change"),
    
#     # User info
#     path("me/", views_api.UserDetailAPIView.as_view(), name="api_user_detail"),
# ]
