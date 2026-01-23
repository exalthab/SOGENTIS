# accounts_users/web/urls/__init__.py
from django.urls import include, path

app_name = "web"

urlpatterns = [
    path("auth/", include(("accounts_users.web.urls.auth_urls", "auth"), namespace="auth")),
    path("registration/", include(("accounts_users.web.urls.registration_urls", "registration"), namespace="registration")),
    path("profile/", include(("accounts_users.web.urls.profile_urls", "profile"), namespace="profile")),
    path("password/", include(("accounts_users.web.urls.password_urls", "password"), namespace="password")),
    path("ajax/", include(("accounts_users.web.urls.ajax_urls", "ajax"), namespace="ajax")),
]


