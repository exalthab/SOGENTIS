# accounts_users/views/activation.py

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def activate_user_from_token(uidb64: str, token: str):
    """
    Active un utilisateur à partir d’un token.
    Retour :
        {
            "user": user | None,
            "status": "success" | "already_active" | "invalid"
        }
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return {"user": None, "status": "invalid"}

    # Token invalide
    if not default_token_generator.check_token(user, token):
        return {"user": user, "status": "invalid"}

    # Déjà actif
    if user.is_active:
        return {"user": user, "status": "already_active"}

    # Activation
    user.is_active = True
    user.save(update_fields=["is_active"])

    return {"user": user, "status": "success"}


def resend_activation_link(request, email: str):
    """
    Renvoie un lien d’activation par email.
    Retour :
        {
            "user": user | None,
            "status": "sent" | "already_active" | "not_found"
        }
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return {"user": None, "status": "not_found"}

    if user.is_active:
        return {"user": user, "status": "already_active"}

    # Génération token + lien
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_url = request.build_absolute_uri(
        reverse(
            "accounts_users_web:activate",
            kwargs={"uidb64": uid, "token": token},
        )
    )

    html_message = render_to_string(
        "accounts_users/emails/account_activation_email.html",
        {
            "user": user,
            "activation_url": activation_url,
        },
    )

    send_mail(
        subject=_("Activation de votre compte SOGENTIS"),
        message=_("Veuillez activer votre compte via le lien reçu."),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )

    return {"user": user, "status": "sent"}







# # accounts_users/views/activation.py

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_decode
# from django.utils.encoding import force_str

# from accounts_users.models.custom_users import CustomUser


# def activate_user_from_token(uidb64: str, token: str):
#     """
#     Retourne un dictionnaire contenant :
#     - user         → l'utilisateur ou None
#     - status       → "success", "already_active", "invalid"
#     """

#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = CustomUser.objects.get(pk=uid)
#     except Exception:
#         return {"user": None, "status": "invalid"}

#     # Vérifier la validité du token
#     if not default_token_generator.check_token(user, token):
#         return {"user": user, "status": "invalid"}

#     # Cas : déjà activé
#     if user.is_active:
#         return {"user": user, "status": "already_active"}

#     # Activation normale
#     user.is_active = True
#     user.save()

#     return {"user": user, "status": "success"}







# # accounts_users/views/activation.py
# from django.contrib.auth.tokens import default_token_generator
# from django.shortcuts import get_object_or_404, render
# from django.utils.http import urlsafe_base64_decode
# from django.utils.translation import gettext_lazy as _
# from django.contrib import messages
# from django.utils.encoding import force_str

# from accounts_users.models.users import CustomUser

# def activate_account_view(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = get_object_or_404(CustomUser, pk=uid)
#     except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#         user = None

#     context = {"user": user}

#     if user is not None and default_token_generator.check_token(user, token):
#         if not user.is_active:
#             user.is_active = True
#             user.save()
#             messages.success(request, _("Votre compte a été activé avec succès."))
#             context["activated"] = True
#             return render(request, "accounts_users/registration/activation_success.html", context)
#         else:
#             # Déjà activé
#             messages.info(request, _("Ce compte est déjà activé."))
#             context["already_active"] = True
#             return render(request, "accounts_users/registration/activation_success.html", context)
#     else:
#         messages.error(request, _("Le lien d'activation est invalide ou expiré."))
#         return render(request, "accounts_users/registration/activation_invalid.html", context)




# # accounts_users/views/activation.py
# from django.contrib.auth.tokens import default_token_generator
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.http import urlsafe_base64_decode
# from django.utils.translation import gettext_lazy as _
# from django.contrib import messages

# from accounts_users.models.users import CustomUser


# def activate_account_view(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = get_object_or_404(CustomUser, pk=uid)
#     except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#         user = None

#     if user and default_token_generator.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, _("Votre compte a été activé avec succès."))
#         return redirect('accounts_users_web:login')
#     else:
#         messages.error(request, _("Le lien d'activation est invalide ou expiré."))
#         return redirect('accounts_users_web:login')






## accounts_users/views/activation.py -> 01/07
# from django.utils.http import urlsafe_base64_decode
# from accounts_users.tokens import account_activation_token
# # from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth import get_user_model
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _
# from django.contrib import messages

# User = get_user_model()

# def activate_account_view(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = get_user_model().objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
#         user = None

#     if user and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, _("Votre compte a été activé. Vous pouvez maintenant vous connecter."))
#         return redirect("accounts_users_web:login")
#     else:
#         messages.error(request, _("Lien d'activation invalide ou expiré."))
#         return redirect("accounts_users_web:signup")










# def activate_account_view(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user and default_token_generator.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, _("Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter."))
#         return redirect('accounts_users_web:login')
#     else:
#         messages.error(request, _("Lien d'activation invalide ou expiré."))
#         return render(request, "accounts_users/registration/activation_failed.html")
