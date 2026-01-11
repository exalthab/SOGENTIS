# accounts_users/web/views/social/social_registration_view.py
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model

from accounts_users.forms.signup_forms import UserSignupForm
from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
from accounts_users.tokens import account_activation_token
from accounts_users.models.phone_otp import PhoneOTP

logger = logging.getLogger(__name__)
User = get_user_model()


def social_register_view(request):
    """
    Vue d'inscription sociale (ONG) avec vérification OTP téléphone.
    """

    excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

    if request.method == "POST":
        user_form = UserSignupForm(request.POST)
        profile_form = SocialRegistrationForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            phone = profile_form.cleaned_data.get("phone_number")

            # Vérification OTP obligatoire
            if not PhoneOTP.objects.filter(phone=phone, is_verified=True).exists():
                messages.error(
                    request,
                    _("Veuillez vérifier votre numéro de téléphone avant de continuer.")
                )
                return redirect("accounts_users_web:social_register")

            try:
                with transaction.atomic():
                    # 1) USER
                    user = user_form.save(commit=False)
                    user.is_active = False
                    user.save()

                    # 2) PROFILE SOCIAL
                    profile_form.save(user=user, commit=True)

                    # 3) EMAIL activation
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = account_activation_token.make_token(user)

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
                            "year": now().year,
                        },
                    )

                    user.email_user(
                        subject=_("Activation de votre compte SOGENTIS"),
                        message=_("Veuillez activer votre compte via le lien reçu."),
                        html_message=html_message,
                    )

                messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
                return redirect("accounts_users_web:login")

            except IntegrityError:
                messages.error(request, _("Un utilisateur avec cet email existe déjà."))
            except Exception as e:
                logger.exception("Erreur inscription sociale : %s", e)
                messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
        else:
            messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

    else:
        user_form = UserSignupForm()
        profile_form = SocialRegistrationForm()

    return render(
        request,
        "accounts_users/registration/social_signup.html",
        {
            "form": user_form,
            "profile_form": profile_form,
            "excluded_profile_fields": excluded_profile_fields,
        },
    )




# # accounts_users/web/views/social/social_registration_view.py
# import logging
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from django.db import transaction, IntegrityError
# from django.contrib.auth import get_user_model

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token
# from dashboard.forms import profile_form

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def social_register_view(request):
#     # Utilisé par le template pour exclure les champs rendus manuellement
#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # 1) USER
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # 2) PROFILE (IMPORTANT : ton form a save(user=...))
#                     profile_form.save(user=user, commit=True)

#                     # 3) EMAIL activation
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)

#                     activation_url = request.build_absolute_uri(
#                         reverse(
#                             "accounts_users_web:activate",
#                             kwargs={"uidb64": uid, "token": token},
#                         )
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {
#                             "user": user,
#                             "activation_url": activation_url,
#                             "year": now().year,
#                         },
#                     )

#                     user.email_user(
#                         subject=_("Activation de votre compte SOGENTIS"),
#                         message=_("Veuillez activer votre compte via le lien reçu."),
#                         html_message=html_message,
#                     )

#                 messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#                 return redirect("accounts_users_web:login")

#             except IntegrityError:
#                 messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             except Exception as e:
#                 logger.exception("Erreur inscription sociale : %s", e)
#                 messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         profile_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_signup.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )
    
#     profile_form = SocialRegistrationForm(request.POST, request.FILES)

#     if profile_form.is_valid():
#         phone = profile_form.cleaned_data.get("phone_number")

#         # Vérification OTP obligatoire
#         if not PhoneOTP.objects.filter(
#             phone=phone,
#             is_verified=True
#         ).exists():
#             messages.error(
#                 request,
#                 _("Veuillez vérifier votre numéro de téléphone avant de continuer.")
#             )
#             return redirect("accounts_users_web:social_signup")





# # accounts_users/web/views/social/social_registration_view.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from django.db import transaction, IntegrityError
# import logging

# from django.contrib.auth import get_user_model
# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def social_register_view(request):

#     excluded_profile_fields = [
#         "terms",
#         "judicial_record",
#         "profile_picture",
#         "phone_number",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         social_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and social_form.is_valid():
#             try:
#                 with transaction.atomic():

#                     # 1️⃣ UTILISATEUR
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # 2️⃣ PROFIL SOCIAL (CORRECT)
#                     social_form.save(user=user)

#                     # 3️⃣ EMAIL D’ACTIVATION
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)

#                     activation_url = request.build_absolute_uri(
#                         reverse(
#                             "accounts_users_web:activate",
#                             kwargs={"uidb64": uid, "token": token},
#                         )
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {
#                             "user": user,
#                             "activation_url": activation_url,
#                             "year": now().year,
#                         },
#                     )

#                     user.email_user(
#                         subject=_("Activation de votre compte SOGENTIS"),
#                         message=_("Veuillez activer votre compte via le lien reçu."),
#                         html_message=html_message,
#                     )

#                 messages.success(
#                     request,
#                     _("Un lien d’activation vous a été envoyé par e-mail.")
#                 )
#                 return redirect("accounts_users_web:login")

#             except IntegrityError:
#                 messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             except Exception as e:
#                 logger.exception(e)
#                 messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         social_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_signup.html",
#         {
#             "form": user_form,
#             "profile_form": social_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )









# # accounts_users/web/views/social/social_registration_view.py 26/12/2025

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from django.db import transaction, IntegrityError
# import logging

# from django.contrib.auth import get_user_model
# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def social_register_view(request):
#     """
#     Inscription sociale publique :
#     - Création d’un utilisateur inactif
#     - Création du profil social
#     - Envoi d’un email d’activation
#     """

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         social_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and social_form.is_valid():
#             try:
#                 with transaction.atomic():

#                     # 1️⃣ UTILISATEUR
#                     # ⚠️ NE PAS appeler set_password ici
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # 2️⃣ PROFIL SOCIAL
#                     social_profile = social_form.save(commit=False)
#                     social_profile.user = user
#                     social_profile.save()

#                     # 3️⃣ EMAIL D’ACTIVATION
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)

#                     activation_url = request.build_absolute_uri(
#                         reverse(
#                             "accounts_users_web:activate",
#                             kwargs={"uidb64": uid, "token": token},
#                         )
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {
#                             "user": user,
#                             "activation_url": activation_url,
#                             "year": now().year,
#                         },
#                     )

#                     user.email_user(
#                         subject=_("Activation de votre compte SOGENTIS"),
#                         message=_("Veuillez activer votre compte via le lien reçu."),
#                         html_message=html_message,
#                     )

#                 messages.success(
#                     request,
#                     _("Un lien d’activation vous a été envoyé par e-mail.")
#                 )
#                 return redirect("accounts_users_web:login")

#             except IntegrityError as e:
#                 logger.error(f"Erreur d'intégrité: {e}")
#                 messages.error(
#                     request,
#                     _("Un utilisateur avec cet email existe déjà.")
#                 )
#             except Exception as e:
#                 logger.error(f"Erreur générale: {e}")
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue. Veuillez réessayer.")
#                 )

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         social_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_signup.html",
#         {
#             "form": user_form,
#             "profile_form": social_form,
#         },
#     )







# # accounts_users/web/views/social/social_registration_view.py
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from django.db import transaction, IntegrityError
# import logging

# # Initialisation du logger
# logger = logging.getLogger(__name__)

# from django.contrib.auth import get_user_model
# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# User = get_user_model()

# def social_register_view(request):
#     """
#     Inscription sociale publique :
#     - Création d’un utilisateur inactif
#     - Création du profil social
#     - Envoi d’un email d’activation
#     """

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         social_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and social_form.is_valid():
#             try:
#                 with transaction.atomic():  # S'assurer que les deux opérations se font ensemble

#                     # --------------------------------------------------
#                     # 1️⃣ UTILISATEUR
#                     # --------------------------------------------------
#                     user = user_form.save(commit=False)
#                     user.set_password(user_form.cleaned_data["password"])
#                     user.is_active = False  # Le compte est inactif au départ
#                     user.save()

#                     # --------------------------------------------------
#                     # 2️⃣ PROFIL SOCIAL
#                     # --------------------------------------------------
#                     social_profile = social_form.save(commit=False)
#                     social_profile.user = user
#                     social_profile.save()

#                     # --------------------------------------------------
#                     # 3️⃣ EMAIL D’ACTIVATION
#                     # --------------------------------------------------
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)

#                     activation_url = request.build_absolute_uri(
#                         reverse(
#                             "accounts_users_web:activate",
#                             kwargs={"uidb64": uid, "token": token},
#                         )
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {
#                             "user": user,
#                             "activation_url": activation_url,
#                             "year": now().year,
#                         },
#                     )

#                     user.email_user(
#                         subject=_("Activation de votre compte SOGENTIS"),
#                         message=_("Veuillez activer votre compte via le lien reçu."),
#                         html_message=html_message,
#                     )

#                 messages.success(
#                     request,
#                     _("Un lien d’activation vous a été envoyé par e-mail.")
#                 )
#                 return redirect("accounts_users_web:login")

#             except IntegrityError as e:
#                 logger.error(f"Erreur d'intégrité: {str(e)}")
#                 messages.error(
#                     request,
#                     _("Une erreur de base de données est survenue. Un utilisateur avec cet email pourrait déjà exister.")
#                 )
#             except Exception as e:
#                 logger.error(f"Erreur générale: {str(e)}")
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue : %s. Veuillez réessayer.") % str(e)
#                 )

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         social_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_signup.html",
#         {
#             "form": user_form,
#             "profile_form": social_form,
#         },
#     )




# # accounts_users/web/views/social/social_registration_view.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from django.db import transaction

# from django.contrib.auth import get_user_model

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# User = get_user_model()


# def social_register_view(request):
#     """
#     Inscription sociale publique :
#     - Création d’un utilisateur inactif
#     - Création du profil social
#     - Envoi d’un email d’activation
#     """

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         social_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and social_form.is_valid():
#             try:
#                 with transaction.atomic():

#                     # --------------------------------------------------
#                     # 1️⃣ UTILISATEUR
#                     # --------------------------------------------------
#                     user = user_form.save(commit=False)
#                     user.set_password(user_form.cleaned_data["password"])
#                     user.is_active = False
#                     user.save()

#                     # --------------------------------------------------
#                     # 2️⃣ PROFIL SOCIAL
#                     # --------------------------------------------------
#                     social_profile = social_form.save(commit=False)
#                     social_profile.user = user
#                     social_profile.save()

#                     # --------------------------------------------------
#                     # 3️⃣ EMAIL D’ACTIVATION
#                     # --------------------------------------------------
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)

#                     activation_url = request.build_absolute_uri(
#                         reverse(
#                             "accounts_users_web:activate",
#                             kwargs={"uidb64": uid, "token": token},
#                         )
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {
#                             "user": user,
#                             "activation_url": activation_url,
#                             "year": now().year,
#                         },
#                     )

#                     user.email_user(
#                         subject=_("Activation de votre compte SOGENTIS"),
#                         message=_("Veuillez activer votre compte via le lien reçu."),
#                         html_message=html_message,
#                     )

#                 messages.success(
#                     request,
#                     _("Un lien d’activation vous a été envoyé par e-mail.")
#                 )
#                 return redirect("accounts_users_web:login")

#             except Exception:
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue. Veuillez réessayer.")
#                 )

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         social_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_signup.html",
#         {
#             "form": user_form,
#             "profile_form": social_form,
#         },
#     )





# # # accounts_users/web/views/social/social_registration_view.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.template.loader import render_to_string
# from django.utils.timezone import now

# from django.contrib.auth import get_user_model

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token
# from accounts_users.models.social.social_profile import SocialProfile

# User = get_user_model()


# def social_register_view(request):
#     """
#     Inscription SOCIALE publique :
#     - Création du User (inactif)
#     - Création du SocialProfile
#     - Envoi email d’activation
#     """

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         social_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and social_form.is_valid():
#             # --------------------------------------------------
#             # 1️⃣ UTILISATEUR
#             # --------------------------------------------------
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data["password"])
#             user.is_active = False
#             user.save()

#             # --------------------------------------------------
#             # 2️⃣ PROFIL SOCIAL
#             # --------------------------------------------------
#             social_profile = social_form.save(commit=False)
#             social_profile.user = user

#             # Sécurité anti-doublon
#             existing = SocialProfile.objects.filter(user=user).first()
#             if existing:
#                 social_profile.pk = existing.pk

#             social_profile.save()

#             # --------------------------------------------------
#             # 3️⃣ EMAIL D’ACTIVATION
#             # --------------------------------------------------
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             token = account_activation_token.make_token(user)

#             activation_url = request.build_absolute_uri(
#                 reverse(
#                     "accounts_users_web:activate",
#                     kwargs={"uidb64": uid, "token": token},
#                 )
#             )

#             html_message = render_to_string(
#                 "accounts_users/emails/account_activation_email.html",
#                 {
#                     "user": user,
#                     "activation_url": activation_url,
#                     "year": now().year,
#                 },
#             )

#             user.email_user(
#                 subject=_("Activation de votre compte SOGENTIS"),
#                 message=_("Veuillez activer votre compte via le lien reçu."),
#                 html_message=html_message,
#             )

#             messages.success(
#                 request,
#                 _("Un lien d’activation vous a été envoyé par e-mail.")
#             )
#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         social_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_signup.html",
#         {
#             "form": user_form,
#             "profile_form": social_form,
#         },
#     )





# # accounts_users/views/social/social_registration_view.py
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from accounts_users.models.social.social_profile import SocialProfile


# class SocialRegistrationForm(forms.ModelForm):
#     """
#     Formulaire unique d’inscription sociale publique.
#     Crée UNIQUEMENT un SocialProfile.
#     """

#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
#     )

#     class Meta:
#         model = SocialProfile
#         exclude = (
#             "user",
#             "is_active_member",
#             "is_validated",
#             "validated_at",
#             "created_at",
#             "updated_at",
#         )

#     # --------------------------------------------------
#     # SAVE OVERRIDE (OBLIGATOIRE)
#     # --------------------------------------------------
#     def save(self, user, commit=True):
#         """
#         Associe explicitement le SocialProfile à l’utilisateur créé.
#         """
#         social_profile = super().save(commit=False)
#         social_profile.user = user

#         if not social_profile.membership_date:
#             social_profile.membership_date = timezone.now().date()

#         social_profile.is_active_member = False
#         social_profile.is_validated = False

#         if commit:
#             social_profile.save()

#         return social_profile






# # accounts_users/web/views/social/social_registration_view.py
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods
# from django.db import transaction

# from accounts_users.forms.social.social_signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm


# # ======================================================
# # INSCRIPTION SOCIALE PUBLIQUE
# # ======================================================
# @require_http_methods(["GET", "POST"])
# def social_register_view(request):
#     """
#     Inscription SOCIALE PUBLIQUE :
#     - Création du compte utilisateur
#     - Création du UserProfile
#     - Création du SocialProfile
#     - Un seul formulaire côté utilisateur
#     """

#     user_form = UserSignupForm(request.POST or None)
#     registration_form = SocialRegistrationForm(
#         request.POST or None,
#         request.FILES or None,
#     )

#     if request.method == "POST":

#         if user_form.is_valid() and registration_form.is_valid():

#             try:
#                 with transaction.atomic():

#                     # 1️⃣ Création utilisateur
#                     user = user_form.save(commit=False)
#                     user.is_active = True  # passer à False si activation email
#                     user.save()

#                     # 2️⃣ Création profils (central + social)
#                     registration_form.save(user=user)

#             except Exception:
#                 messages.error(
#                     request,
#                     _(
#                         "Une erreur est survenue lors de l’inscription sociale. "
#                         "Veuillez réessayer."
#                     )
#                 )
#                 return redirect("accounts_users_web:social_register")

#             messages.success(
#                 request,
#                 _(
#                     "Votre inscription sociale a été enregistrée avec succès. "
#                     "Vous pouvez maintenant vous connecter. "
#                     "Votre adhésion sera validée après examen."
#                 )
#             )

#             return redirect("accounts_users_web:login")

#         messages.error(
#             request,
#             _("Veuillez corriger les erreurs du formulaire.")
#         )

#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "user_form": user_form,
#             "registration_form": registration_form,
#             "auth_pole": "social",
#         },
#     )
