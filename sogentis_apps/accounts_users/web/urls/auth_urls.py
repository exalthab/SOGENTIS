# accounts_users/web/urls/auth_urls.py
from django.urls import path
from accounts_users.web.views.auth_login_choice import auth_choice_view
from accounts_users.web.views import auth_login_web_views
from accounts_users.web.views.auth_login_web_views import login_view

app_name = "auth"

urlpatterns = [
    # HUB (canonique)
    path("", auth_choice_view, name="choice"),
    # alias ancien - accounts/web/auth/
    path("choice/", auth_choice_view, name="auth_choice"),

    # /accounts/web/auth/login/
    path("login/", auth_login_web_views.login_view, name="login"),

    # /accounts/web/auth/login/social/
    path("login/social/", login_view, name="social_login"),

    # /accounts/web/auth/login/economic/
    path("login/economic/", login_view, name="login_economic"),

    # /accounts/web/auth/logout/
    path("logout/", auth_login_web_views.logout_view, name="logout"),
]






# # accounts_users/web/urls/auth_urls.py
# from django.urls import path
# from accounts_users.web.views.auth_login_choice import auth_choice_view
# from accounts_users.web.views import auth_login_web_views
# from accounts_users.web.views.auth_login_web_views import login_view

# app_name = "auth"

# urlpatterns = [
#     path("auth/", auth_choice_view, name="auth_choice"),
#     path("login/", auth_login_web_views.login_view, name="login"),
#     path("login/social/", login_view, name="social_login"),
#     path("login/economic/", login_view, name="login_economic"),
#     path("logout/", auth_login_web_views.logout_view, name="logout"),
# ]
