# accounts_users/web/urls/ajax_urls.py
from django.urls import path
from accounts_users.web.views.validation import check_email_availability
from accounts_users.web.views.email_otp_views import send_email_otp, verify_email_otp

app_name = "ajax"

urlpatterns = [
    path("check-email/", check_email_availability, name="check_email"),
    path("email/send-otp/", send_email_otp, name="send_email_otp"),
    path("email/verify-otp/", verify_email_otp, name="verify_email_otp"),
]
