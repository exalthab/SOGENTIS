# accounts_users/web/urls.py

from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from accounts_users.web.views import (
    auth_web_views, registration_views, profile_views
)
from accounts_users.web.views.registration_views import activate_view, resend_activation_view
from accounts_users.web.views.password_views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

app_name = "accounts_users_web"

urlpatterns = [
    # Authentification
    path("login/", auth_web_views.login_view, name="login"),
    path("logout/", auth_web_views.logout_view, name="logout"),

    # Inscription & activation
    path("signup/", registration_views.signup_view, name="signup"),
    path("signup/confirmation/", TemplateView.as_view(
        template_name="accounts_users/registration/signup_done.html"
    ), name="signup_done"),
    path("activer/<uidb64>/<token>/", activate_view, name="activate"),
    path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),

    # Profil (état en attente)
    path('profile/pending/', profile_views.profile_pending_notice, name='profile_pending_notice'),

    # --- Password change (connecté) ---
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts_users/registration/password_change_form.html'
    ), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts_users/registration/password_change_done.html'
    ), name='password_change_done'),

    # --- Password reset (oubli, 100% CBV custom) ---
    path(
        'password_reset/',
        CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        CustomPasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm"
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete"
    ),

    # Si besoin, active la vue custom function-based ci-dessous avec un nom UNIQUE, sans collision
    # path("password-reset-custom/", password_views.password_reset_request, name="custom_password_reset"),
]









# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views
# from accounts_users.web.views import (
#     auth_web_views, password_views, registration_views, profile_views
# )
# from accounts_users.web.views.registration_views import activate_view, resend_activation_view

# app_name = "accounts_users_web"

# urlpatterns = [
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),
#     path("signup/", registration_views.signup_view, name="signup"),
#     path("signup/confirmation/", TemplateView.as_view(
#         template_name="accounts_users/registration/signup_done.html"
#     ), name="signup_done"),
#     path("activer/<uidb64>/<token>/", activate_view, name="activate"),
#     path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),
#     path('profile/pending/', profile_views.profile_pending_notice, name='profile_pending_notice'),

#     # FLOW DJANGO natif (conseillé) pour la réinitialisation
#     path("password_reset/", auth_views.PasswordResetView.as_view(
#             template_name="accounts_users/registration/password_reset_form.html"
#         ), name="password_reset"),
#     path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
#             template_name="accounts_users/registration/password_reset_done.html"
#         ), name="password_reset_done"),
#     path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
#             template_name="accounts_users/registration/password_reset_confirm.html"
#         ), name="password_reset_confirm"),
#     path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
#             template_name="accounts_users/registration/password_reset_complete.html"
#         ), name="password_reset_complete"),

#     # (optionnel) Si tu veux vraiment garder ta vue custom, renomme-la pour éviter tout conflit !
#     path("password-reset/", password_views.password_reset_request, name="custom_password_reset"),
# ]






#29/07/2025
# from django.urls import path
# from django.views.generic import TemplateView
# from accounts_users.web.views import (
#     auth_web_views, password_views, registration_views, profile_views
# )
# from accounts_users.web.views.registration_views import activate_view, resend_activation_view

# app_name = "accounts_users_web"

# urlpatterns = [
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),
#     path("signup/", registration_views.signup_view, name="signup"),
#     path("password-reset/", password_views.password_reset_request, name="password_reset"),

#     path("signup/confirmation/", TemplateView.as_view(
#         template_name="accounts_users/registration/signup_done.html"
#     ), name="signup_done"),

#     path("activer/<uidb64>/<token>/", activate_view, name="activate"),
#     path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),

#     path('profile/pending/', profile_views.profile_pending_notice, name='profile_pending_notice'),
# ]
