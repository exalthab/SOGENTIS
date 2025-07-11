from django.shortcuts import render
from accounts_users.forms.password_forms import CustomPasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            for user in users:
                context = {
                    "email": user.email,
                    "domain": request.get_host(),
                    "site_name": "Sogentis",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": "https" if request.is_secure() else "http",
                }
                subject = render_to_string("accounts_users/registration/password_reset_subject.txt", context)
                subject = "".join(subject.splitlines())
                email_body = render_to_string("accounts_users/registration/password_reset_email.html", context)
                send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])
    else:
        form = CustomPasswordResetForm()
    return render(request, "accounts_users/registration/password_reset.html", {"form": form})
