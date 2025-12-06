# accounts_users/web/views/activation_web_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from accounts_users.tokens import account_activation_token

User = get_user_model()

def activate_account_view(request, uidb64, token):
    """
    Active le compte utilisateur si le token est valide.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, _("Lien d'activation invalide."))
        return redirect("accounts_users_web:login")  # Redirige proprement

    if account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, _("Votre compte a été activé avec succès."))
        return redirect("accounts_users_web:login")
    else:
        messages.error(request, _("Lien d’activation invalide ou expiré."))
        return redirect("accounts_users_web:login")
