# accounts_users/views/activation.py
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from accounts_users.models.users import CustomUser


def activate_account_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(CustomUser, pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, _("Votre compte a été activé avec succès."))
        return redirect('accounts_users_web:login')
    else:
        messages.error(request, _("Le lien d'activation est invalide ou expiré."))
        return redirect('accounts_users_web:login')






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
