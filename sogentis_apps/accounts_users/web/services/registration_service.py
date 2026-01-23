from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts_users.tokens import account_activation_token
from accounts_users.models.registration import (
    RegistrationApplication,
    RegistrationCategory,
    RegistrationDocument,
    RegistrationDocType,
)

UserModel = get_user_model()


def create_inactive_user_from_cleaned(cleaned: dict):
    email = cleaned["email"]
    user = UserModel(email=email)
    # set attributes only if exist
    for attr in ("first_name", "last_name"):
        if hasattr(user, attr):
            setattr(user, attr, cleaned.get(attr, ""))
    # username fallback if needed
    if hasattr(user, "username") and not getattr(user, "username", None):
        user.username = email.split("@")[0]

    user.set_password(cleaned["password1"])
    user.is_active = False
    user.save()
    return user


def send_activation_email(request, user) -> bool:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    activation_url = request.build_absolute_uri(
        reverse("accounts_users:web:registration:activate", kwargs={"uidb64": uidb64, "token": token})
    )

    ctx = {"user": user, "activation_url": activation_url, "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS")}
    subject = "Activation de votre compte"

    html = render_to_string("accounts_users/registration/account_activation_email.html", ctx)
    txt = render_to_string("accounts_users/registration/account_activation_email.txt", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=txt,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[user.email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)
    return True


def create_application_and_docs(*, user, category, track: str, payload: dict, files_map: dict):
    app = RegistrationApplication.objects.create(
        user=user,
        category=category,
        track=track or "",
        payload=payload,
    )

    # files_map = {"ID_FRONT": file, ...}
    for doc_type, f in (files_map or {}).items():
        if f:
            RegistrationDocument.objects.create(application=app, doc_type=doc_type, file=f)

    return app
