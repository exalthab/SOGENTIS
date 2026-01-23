# accounts_users/web/urls/password_urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts_users.web.views.password_views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

app_name = "password"

urlpatterns = [
    # Password change (connecté)
    path(
        "change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts_users/registration/password_change_form.html"
        ),
        name="password_change",
    ),
    path(
        "change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts_users/registration/password_change_done.html"
        ),
        name="password_change_done",
    ),

    # Password reset (oubli)
    path("reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/complete/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
