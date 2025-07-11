from django.urls import path
from django.views.generic import TemplateView
from accounts_users.web.views import (
    auth_web_views, password_views, registration_views
)
from accounts_users.web.views.registration_views import activate_view, resend_activation_view
from accounts_users.web.views.profile_views import profile_pending_notice
from django.views.generic import TemplateView


app_name = "accounts_users_web"

urlpatterns = [
    path("login/", auth_web_views.login_view, name="login"),
    path("logout/", auth_web_views.logout_view, name="logout"),
    path("signup/", registration_views.signup_view, name="signup"),
    path("password-reset/", password_views.password_reset_request, name="password_reset"),
    # path("confirmation-envoyee/", TemplateView.as_view(
    # template_name="accounts_users/registration/confirmation_sent.html"),
    # name="confirmation_sent"),
    path("signup/confirmation/", TemplateView.as_view(
        template_name="accounts_users/registration/signup_done.html"
    ), name="signup_done"),
    path("activer/<uidb64>/<token>/", registration_views.activate_view, name="activate"),
    path("activer/<uidb64>/<token>/", activate_view, name="activate"),
    path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),
    path('profile/pending/', profile_pending_notice, name='profile_pending_notice'),


]
