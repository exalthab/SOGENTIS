# accounts_users/web/views/activation_web_views.py
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from accounts_users.views.activation import (
    activate_user_from_token,
    resend_activation_link,  # service métier
)


def activate_account_view(request, uidb64, token):
    """
    Vue orientée interface :
    - Appelle la logique d’activation
    - Affiche les templates adaptés
    """
    try:
        result = activate_user_from_token(uidb64, token)
    except Exception:
        messages.error(request, _("Une erreur est survenue lors de l’activation."))
        return render(request, "accounts_users/registration/activation_invalid.html", {})

    user = result.get("user")
    status = result.get("status")
    context = {"user": user}

    if status == "success":
        messages.success(
            request,
            _("Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter.")
        )
        context["activated"] = True
        return render(request, "accounts_users/registration/activation_success.html", context)

    if status == "already_active":
        messages.info(
            request,
            _("Ce compte est déjà activé. Vous pouvez vous connecter.")
        )
        context["already_active"] = True
        return render(request, "accounts_users/registration/activation_success.html", context)

    messages.error(request, _("Le lien d’activation est invalide ou a expiré."))
    return render(request, "accounts_users/registration/activation_invalid.html", context)


def resend_activation_view(request):
    """
    Renvoi du lien d’activation (vue UI).
    Attend un POST avec 'email'.
    """
    if request.method != "POST":
        return redirect("accounts_users:web:auth:login")

    email = (request.POST.get("email") or "").strip().lower()
    if not email:
        messages.error(request, _("Veuillez fournir une adresse e-mail."))
        return redirect("accounts_users:web:auth:login")

    try:
        result = resend_activation_link(request=request, email=email)
    except Exception:
        messages.error(request, _("Impossible d’envoyer le lien d’activation pour le moment."))
        return redirect("accounts_users:web:auth:login")

    status = result.get("status")

    if status == "sent":
        messages.success(request, _("Un nouveau lien d’activation vous a été envoyé par e-mail."))
    elif status == "already_active":
        messages.info(request, _("Ce compte est déjà activé. Vous pouvez vous connecter."))
    elif status == "not_found":
        messages.error(request, _("Aucun compte trouvé avec cette adresse e-mail."))
    else:
        messages.error(request, _("Impossible d’envoyer le lien d’activation."))

    return redirect("accounts_users:web:auth:login")







# # accounts_users/web/views/activation_web_views.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _

# from accounts_users.views.activation import activate_user_from_token


# def activate_account_view(request, uidb64, token):
#     """
#     Vue orientée interface : rend templates ou redirige vers login.
#     """

#     result = activate_user_from_token(uidb64, token)
#     user = result["user"]
#     status = result["status"]

#     context = {"user": user}

#     # -----------------------------
#     # 🔹 Succès : compte activé
#     # -----------------------------
#     if status == "success":
#         messages.success(request, _("Votre compte a été activé avec succès."))
#         context["activated"] = True
#         return render(request, "accounts_users/registration/activation_success.html", context)

#     # -----------------------------
#     # 🔹 Compte déjà activé
#     # -----------------------------
#     if status == "already_active":
#         messages.info(request, _("Ce compte est déjà activé."))
#         context["already_active"] = True
#         return render(request, "accounts_users/registration/activation_success.html", context)

#     # -----------------------------
#     # ❌ Lien invalide / expiré
#     # -----------------------------
#     messages.error(request, _("Lien d’activation invalide ou expiré."))
#     return render(request, "accounts_users/registration/activation_invalid.html", context)






# # accounts_users/web/views/activation_web_views.py
# from django.shortcuts import render, redirect
# from django.contrib.auth import get_user_model
# from django.utils.http import urlsafe_base64_decode
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from accounts_users.tokens import account_activation_token

# User = get_user_model()

# def activate_account_view(request, uidb64, token):
#     """
#     Active le compte utilisateur si le token est valide.
#     """
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         messages.error(request, _("Lien d'activation invalide."))
#         return redirect("accounts_users_web:login")  # Redirige proprement

#     if account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, _("Votre compte a été activé avec succès."))
#         return redirect("accounts_users_web:login")
#     else:
#         messages.error(request, _("Lien d’activation invalide ou expiré."))
#         return redirect("accounts_users_web:login")
