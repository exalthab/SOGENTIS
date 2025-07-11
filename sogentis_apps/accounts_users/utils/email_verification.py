from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator

def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    activation_link = request.build_absolute_uri(
        reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
    )

    subject = _("Activez votre compte SOGENTIS")
    message = render_to_string("accounts_users/registration/email_activation.html", {
        "user": user,
        "activation_link": activation_link,
        "domain": domain,
    })

    send_mail(
        subject,
        message,
        "noreply@sogentis.org",  # Adresse expéditrice
        [user.email],
        fail_silently=False,
    )
