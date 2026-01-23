# accounts_users/web/views/registration_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

from accounts_users.views.registration import create_user_and_profile
from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm


# -----------------------------------------------------
#  INSCRIPTION
# -----------------------------------------------------
def signup_view(request):
    if request.method == "POST":

        user, profile, uid, token = create_user_and_profile(
            request.POST,
            request.POST,
            files=request.FILES
        )

        # Erreur de formulaire
        if user is None:
            return render(request, "accounts_users/registration/signup.html", {
                "form": UserSignupForm(request.POST),
                "profile_form": UserProfileForm(request.POST, request.FILES),
            })

        # URL d’activation
        activation_url = request.build_absolute_uri(
            reverse("accounts_users:web:registration:activate", kwargs={"uidb64": uid, "token": token})
        )

        # ---------------------------------------------------------
        # MODE DEV → afficher le lien directement
        # ---------------------------------------------------------
        if getattr(settings, "IS_DEV", False):
            messages.info(request, f"[DEV] Lien d'activation : {activation_url}")
        else:
            # Email HTML réel
            html_message = render_to_string(
                "accounts_users/emails/account_activation_email.html",
                {"user": user, "activation_url": activation_url}
            )

            send_mail(
                subject=_("Activation de votre compte"),
                message=_("Veuillez cliquer sur le lien pour activer votre compte."),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message
            )

        messages.success(request, _("Votre inscription est enregistrée. Vérifiez votre email."))
        return redirect("accounts_users:web:auth:login")

    return render(request, "accounts_users/registration/signup.html", {
        "form": UserSignupForm(),
        "profile_form": UserProfileForm(),
    })


# -----------------------------------------------------
#  ACTIVATION
# -----------------------------------------------------
from accounts_users.views.registration import activate_user_account


def activate_view(request, uidb64, token):
    user = activate_user_account(uidb64, token)

    if user:
        messages.success(request, _("Votre compte a été activé avec succès !"))
        return redirect("accounts_users:web:auth:login")

    messages.error(request, _("Le lien d'activation est invalide ou expiré."))
    return redirect("accounts_users:web:auth:signup")


# -----------------------------------------------------
#  RÉ-ENVOI D’ACTIVATION
# -----------------------------------------------------
def resend_activation_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, _("Aucun compte trouvé avec cet email."))
            return redirect("accounts_users:web:registration:resend_activation")

        if user.is_active:
            messages.info(request, _("Ce compte est déjà actif."))
            return redirect("accounts_users:web:auth:login")

        # Recréation du lien
        from accounts_users.views.registration import generate_activation_token
        uid, token = generate_activation_token(user)

        activation_url = request.build_absolute_uri(
            reverse("accounts_users:web:registration:activate", kwargs={"uidb64": uid, "token": token})
        )

        # Envoi email
        html_message = render_to_string(
            "accounts_users/emails/account_activation_email.html",
            {"user": user, "activation_url": activation_url}
        )

        send_mail(
            _("Activation de votre compte"),
            _("Voici votre nouveau lien d'activation."),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message
        )

        messages.success(request, _("Un nouveau lien d’activation a été envoyé."))
        return redirect("accounts_users:web:auth:login")

    return render(request, "accounts_users/registration/resend_activation.html")
