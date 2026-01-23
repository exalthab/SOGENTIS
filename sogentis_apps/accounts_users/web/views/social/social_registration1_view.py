# # accounts_users/web/views/social/social_registration_view.py
# from __future__ import annotations

# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import mark_profile_email_verified
# from accounts_users.tokens import account_activation_token
# from accounts_users.web.views._helpers import build_auth_context, validate_latest_email_otp_or_add_error

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
#     ctx = {
#         "form": user_form,
#         "profile_form": profile_form,
#         "excluded_profile_fields": excluded_profile_fields,
#         **build_auth_context("social"),
#     }
#     return render(request, "accounts_users/registration/social_register_form.html", ctx)


# def generate_social_code(role_code: str | None) -> str:
#     """
#     Génère un code court type M001 / V002 / D003 / I004.
#     """
#     role_code = (role_code or "").upper().strip()
#     prefix_map = {"MEMBER": "M", "VOLUNTEER": "V", "SPONSOR": "D", "INSTITUTION": "I"}
#     prefix = prefix_map.get(role_code, "U")

#     if role_code:
#         count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     else:
#         count = SocialProfile.objects.count() + 1

#     return f"{prefix}{count:03}"


# def social_register_view(request):
#     """
#     Inscription sociale:
#     1) Form user + profil
#     2) Vérification OTP email (DB EmailOTP)
#     3) Création user inactif + profil social
#     4) Envoi email d’activation
#     """
#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if not (user_form.is_valid() and profile_form.is_valid()):
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         email = (user_form.cleaned_data.get("email") or "").strip().lower()
#         otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#         if not validate_latest_email_otp_or_add_error(
#             request,
#             email=email,
#             otp_code=otp_code,
#             form=user_form,
#             field_name="email_otp_code",
#         ):
#             messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         try:
#             with transaction.atomic():
#                 user = user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 social_profile = profile_form.save(commit=False)
#                 social_profile.user = user

#                 role_code = None
#                 if getattr(social_profile, "membership_role", None):
#                     role_code = getattr(social_profile.membership_role, "code", None)

#                 social_profile.social_registration_code = generate_social_code(role_code)

#                 # (optionnel) si ton modèle a un champ email: s'assurer qu'il reflète celui du user
#                 if hasattr(social_profile, "email") and not getattr(social_profile, "email", ""):
#                     try:
#                         social_profile.email = user.email
#                     except Exception:
#                         pass

#                 social_profile.save()

#                 # marquer email vérifié si profil existe déjà / champs disponibles
#                 try:
#                     mark_profile_email_verified(email)
#                 except Exception:
#                     pass

#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)
#                 activation_url = request.build_absolute_uri(
#                     reverse("accounts_users:web:activate", kwargs={"uidb64": uid, "token": token})
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {"user": user, "activation_url": activation_url, "year": now().year},
#                 )

#                 from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None
#                 send_mail(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     from_email=from_email,
#                     recipient_list=[user.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )

#             messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#             return redirect("accounts_users:web:social_login")  # conserve ton BG social

#         except IntegrityError:
#             logger.warning("Inscription sociale: email déjà utilisé")
#             user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#             messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         except Exception as e:
#             logger.exception("Erreur inscription sociale : %s", e)
#             messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#     # GET
#     return _render_form(
#         request,
#         user_form=UserSignupForm(),
#         profile_form=SocialRegistrationForm(),
#         excluded_profile_fields=excluded_profile_fields,
#     )






# # accounts_users/web/views/social/social_registration_view.py/ok/12-01-2026
# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import mark_profile_email_verified
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#             "auth_pole": "social",          # ✅ important pour BG + titres
#             "login_context": "social",      # ✅ utile si tu l'utilises ailleurs
#         },
#     )


# def generate_social_code(role_code: str | None) -> str:
#     role_code = (role_code or "").upper()
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get(role_code, "U")
#     count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# def _validate_email_otp(request, *, email: str, otp_code: str, user_form: UserSignupForm) -> bool:
#     otp_code = (otp_code or "").strip()
#     if not otp_code:
#         user_form.add_error("email_otp_code", _("Code OTP manquant."))
#         return False

#     sess_email = request.session.get("otp_email")
#     if sess_email and sess_email != email:
#         user_form.add_error("email_otp_code", _("Tentative non autorisée."))
#         return False

#     try:
#         otp = EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#         return False

#     if otp.is_expired_now():
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         user_form.add_error("email_otp_code", _("Le code OTP est expiré."))
#         return False

#     if otp.code != otp_code:
#         otp.register_attempt()
#         if getattr(otp, "is_expired", False):
#             user_form.add_error("email_otp_code", _("Trop de tentatives. Veuillez redemander un nouveau code."))
#         else:
#             user_form.add_error("email_otp_code", _("Code OTP incorrect."))
#         return False

#     try:
#         otp.verify()
#     except Exception:
#         user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#         return False

#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)
#     request.session.modified = True
#     return True


# def social_register_view(request):
#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if not (user_form.is_valid() and profile_form.is_valid()):
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         email = (user_form.cleaned_data.get("email") or "").strip().lower()
#         otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#         if not _validate_email_otp(request, email=email, otp_code=otp_code, user_form=user_form):
#             messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         try:
#             with transaction.atomic():
#                 user = user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 social_profile = profile_form.save(commit=False)
#                 social_profile.user = user

#                 role_code = None
#                 if getattr(social_profile, "membership_role", None):
#                     role_code = getattr(social_profile.membership_role, "code", None)

#                 social_profile.social_registration_code = generate_social_code(role_code)
#                 social_profile.save()

#                 try:
#                     mark_profile_email_verified(email)
#                 except Exception:
#                     pass

#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)
#                 activation_url = request.build_absolute_uri(
#                     reverse("accounts_users_web:activate", kwargs={"uidb64": uid, "token": token})
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {"user": user, "activation_url": activation_url, "year": now().year},
#                 )

#                 from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None

#                 send_mail(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     from_email=from_email,
#                     recipient_list=[user.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )

#             messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#             return redirect("accounts_users_web:social_login")  # ✅ pour garder le BG social

#         except IntegrityError:
#             logger.warning("Email déjà utilisé")
#             user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#             messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )
#         except Exception as e:
#             logger.exception("Erreur inscription sociale : %s", e)
#             messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()
#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         excluded_profile_fields=excluded_profile_fields,
#     )






# # accounts_users/web/views/social/social_registration_view.py
# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import mark_profile_email_verified
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )


# def generate_social_code(role_code: str | None) -> str:
#     role_code = (role_code or "").upper()
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get(role_code, "U")
#     count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# def _validate_email_otp(request, *, email: str, otp_code: str, user_form: UserSignupForm) -> bool:
#     otp_code = (otp_code or "").strip()
#     if not otp_code:
#         user_form.add_error("email_otp_code", _("Code OTP manquant."))
#         return False

#     sess_email = request.session.get("otp_email")
#     if sess_email and sess_email != email:
#         user_form.add_error("email_otp_code", _("Tentative non autorisée."))
#         return False

#     try:
#         otp = EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#         return False

#     if otp.is_expired_now():
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         user_form.add_error("email_otp_code", _("Le code OTP est expiré."))
#         return False

#     if otp.code != otp_code:
#         otp.register_attempt()
#         if otp.is_expired:
#             user_form.add_error("email_otp_code", _("Trop de tentatives. Veuillez redemander un nouveau code."))
#         else:
#             user_form.add_error("email_otp_code", _("Code OTP incorrect."))
#         return False

#     try:
#         otp.verify()
#     except Exception:
#         user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#         return False

#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)
#     request.session.modified = True
#     return True


# def social_register_view(request):
#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if not (user_form.is_valid() and profile_form.is_valid()):
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         email = (user_form.cleaned_data.get("email") or "").strip().lower()
#         otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#         if not _validate_email_otp(request, email=email, otp_code=otp_code, user_form=user_form):
#             messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         try:
#             with transaction.atomic():
#                 user = user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 social_profile = profile_form.save(commit=False)
#                 social_profile.user = user

#                 role_code = None
#                 if getattr(social_profile, "membership_role", None):
#                     role_code = getattr(social_profile.membership_role, "code", None)

#                 social_profile.social_registration_code = generate_social_code(role_code)
#                 social_profile.save()

#                 try:
#                     mark_profile_email_verified(email)
#                 except Exception:
#                     pass

#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)
#                 activation_url = request.build_absolute_uri(
#                     reverse("accounts_users_web:activate", kwargs={"uidb64": uid, "token": token})
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {"user": user, "activation_url": activation_url, "year": now().year},
#                 )

#                 from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None

#                 send_mail(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     from_email=from_email,
#                     recipient_list=[user.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )

#             messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#             return redirect("accounts_users_web:login")

#         except IntegrityError:
#             logger.warning("Email déjà utilisé")
#             user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#             messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )
#         except Exception as e:
#             logger.exception("Erreur inscription sociale : %s", e)
#             messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()
#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         excluded_profile_fields=excluded_profile_fields,
#     )





# # accounts_users/web/views/social/social_registration_view.py
# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import mark_profile_email_verified
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# # ======================================================
# # 🔵 HELPERS
# # ======================================================
# def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )


# def generate_social_code(role_code: str | None) -> str:
#     """
#     Génère un code social simple (ex: M001, V014, etc.)
#     """
#     role_code = (role_code or "").upper()
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get(role_code, "U")
#     count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# def _validate_email_otp(request, *, email: str, otp_code: str, user_form: UserSignupForm) -> bool:
#     """
#     Valide le OTP email à partir du modèle EmailOTP.
#     - prend le dernier OTP non expiré/non vérifié
#     - vérifie expiration + tentatives
#     - compare le code
#     - marque vérifié si OK
#     Retourne True si OK, sinon ajoute l'erreur au form et retourne False.
#     """
#     otp_code = (otp_code or "").strip()

#     if not otp_code:
#         user_form.add_error("email_otp_code", _("Code OTP manquant."))
#         return False

#     # Sécurité: si on a lié un email en session lors de l'envoi OTP, il doit matcher
#     sess_email = request.session.get("otp_email")
#     if sess_email and sess_email != email:
#         user_form.add_error("email_otp_code", _("Tentative non autorisée."))
#         return False

#     try:
#         otp = EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#         ).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#         return False

#     if otp.is_expired_now():
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         user_form.add_error("email_otp_code", _("Le code OTP est expiré."))
#         return False

#     if otp.code != otp_code:
#         otp.register_attempt()
#         if otp.is_expired:
#             user_form.add_error("email_otp_code", _("Trop de tentatives. Veuillez redemander un nouveau code."))
#         else:
#             user_form.add_error("email_otp_code", _("Code OTP incorrect."))
#         return False

#     # OK
#     try:
#         otp.verify()
#     except Exception:
#         user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#         return False

#     # Nettoyage session OTP (envoi/verif)
#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)
#     request.session.modified = True

#     return True


# # ======================================================
# # 🔵 INSCRIPTION SOCIALE
# # ======================================================
# def social_register_view(request):
#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if not (user_form.is_valid() and profile_form.is_valid()):
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         email = (user_form.cleaned_data.get("email") or "").strip().lower()
#         otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#         # -------------------------------------------------
#         # 0) VALIDATION OTP EMAIL (obligatoire)
#         # -------------------------------------------------
#         if not _validate_email_otp(request, email=email, otp_code=otp_code, user_form=user_form):
#             messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         # -------------------------------------------------
#         # 1) CRÉATION USER + PROFIL + MAIL ACTIVATION
#         # -------------------------------------------------
#         try:
#             with transaction.atomic():
#                 # 1️⃣ USER (inactive tant que lien activation non cliqué)
#                 user = user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 # 2️⃣ SOCIAL PROFILE
#                 social_profile = profile_form.save(commit=False)
#                 social_profile.user = user

#                 role_code = None
#                 if getattr(social_profile, "membership_role", None):
#                     role_code = getattr(social_profile.membership_role, "code", None)

#                 social_profile.social_registration_code = generate_social_code(role_code)
#                 social_profile.save()

#                 # (optionnel/safe) marquer email vérifié côté profils si tu as ce champ/logic
#                 try:
#                     mark_profile_email_verified(email)
#                 except Exception:
#                     pass

#                 # 3️⃣ EMAIL ACTIVATION
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)
#                 activation_url = request.build_absolute_uri(
#                     reverse("accounts_users_web:activate", kwargs={"uidb64": uid, "token": token})
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {"user": user, "activation_url": activation_url, "year": now().year},
#                 )

#                 from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None

#                 send_mail(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     from_email=from_email,
#                     recipient_list=[user.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )

#             messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#             return redirect("accounts_users_web:login")

#         except IntegrityError:
#             logger.warning("Email déjà utilisé")
#             user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#             messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )
#         except Exception as e:
#             logger.exception("Erreur inscription sociale : %s", e)
#             messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#     # GET
#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()
#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         excluded_profile_fields=excluded_profile_fields,
#     )





# # accounts_users/web/views/social/social_registration_view.py
# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import mark_profile_email_verified
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# # ======================================================
# # 🔵 GÉNÉRATION DU CODE SOCIAL
# # ======================================================
# def generate_social_code(role_code: str | None) -> str:
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get((role_code or "").upper(), "U")
#     count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# # ======================================================
# # 🔵 INSCRIPTION SOCIALE
# # ======================================================
# def social_register_view(request):
#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             email = (user_form.cleaned_data.get("email") or "").strip().lower()
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             # -------------------------------------------------
#             # 0) VALIDATION OTP EMAIL (obligatoire)
#             # -------------------------------------------------
#             try:
#                 otp = EmailOTP.objects.filter(
#                     email=email,
#                     is_verified=False,
#                     is_expired=False,
#                 ).latest("created_at")
#             except EmailOTP.DoesNotExist:
#                 user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#                 messages.error(request, _("Le code OTP est invalide ou expiré."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_register_form.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#             if otp.is_expired_now():
#                 otp.is_expired = True
#                 otp.save(update_fields=["is_expired"])
#                 user_form.add_error("email_otp_code", _("Le code OTP est expiré."))
#                 messages.error(request, _("Le code OTP est expiré."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_register_form.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#             if otp.code != otp_code:
#                 otp.register_attempt()
#                 user_form.add_error("email_otp_code", _("Code OTP incorrect."))
#                 messages.error(request, _("Code OTP incorrect."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_register_form.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#             # OK -> vérifie OTP (sets verified_at)
#             try:
#                 otp.verify()
#             except Exception:
#                 user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#                 messages.error(request, _("Le code OTP est invalide ou expiré."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_register_form.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#             # Nettoyage session OTP
#             request.session.pop("otp_email", None)
#             request.session.pop("otp_last_sent_at_email", None)
#             request.session.modified = True

#             # -------------------------------------------------
#             # 1) CRÉATION USER + PROFIL + MAIL ACTIVATION
#             # -------------------------------------------------
#             try:
#                 with transaction.atomic():
#                     # 1️⃣ USER
#                     user = user_form.save(commit=False)
#                     user.is_active = False  # activation par email (token)
#                     user.save()

#                     # 2️⃣ SOCIAL PROFILE
#                     social_profile = profile_form.save(commit=False)
#                     social_profile.user = user

#                     role_code = None
#                     if getattr(social_profile, "membership_role", None):
#                         role_code = getattr(social_profile.membership_role, "code", None)

#                     social_profile.social_registration_code = generate_social_code(role_code)
#                     social_profile.save()

#                     # (optionnel) marquer l’email comme vérifié côté profils (safe)
#                     try:
#                         mark_profile_email_verified(email)
#                     except Exception:
#                         pass

#                     # 3️⃣ EMAIL ACTIVATION
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)
#                     activation_url = request.build_absolute_uri(
#                         reverse("accounts_users_web:activate", kwargs={"uidb64": uid, "token": token})
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {"user": user, "activation_url": activation_url, "year": now().year},
#                     )

#                     if settings.DEFAULT_FROM_EMAIL:
#                         send_mail(
#                             subject=_("Activation de votre compte SOGENTIS"),
#                             message=_("Veuillez activer votre compte via le lien reçu."),
#                             from_email=settings.DEFAULT_FROM_EMAIL,
#                             recipient_list=[user.email],
#                             html_message=html_message,
#                         )
#                     else:
#                         user.email_user(
#                             subject=_("Activation de votre compte SOGENTIS"),
#                             message=_("Veuillez activer votre compte via le lien reçu."),
#                             html_message=html_message,
#                         )

#                 messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#                 return redirect("accounts_users_web:login")

#             except IntegrityError:
#                 logger.warning("Email déjà utilisé")
#                 user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#                 messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             except Exception as e:
#                 logger.exception("Erreur inscription sociale : %s", e)
#                 messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#         return render(
#             request,
#             "accounts_users/registration/social_register_form.html",
#             {
#                 "form": user_form,
#                 "profile_form": profile_form,
#                 "excluded_profile_fields": excluded_profile_fields,
#             },
#         )

#     # GET
#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()
#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )







# # accounts_users/web/views/social/social_registration_view.py
# import logging
# import json

# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.conf import settings
# from django.db import IntegrityError, transaction
# from django.http import JsonResponse
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_POST

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.services.email_otp_service import create_email_otp, mark_profile_email_verified

# logger = logging.getLogger(__name__)
# User = get_user_model()

# EMAIL_VERIFICATION_ENABLED = True


# # ======================================================
# # 🔵 GÉNÉRATION DU CODE SOCIAL
# # ======================================================
# def generate_social_code(role_code: str | None) -> str:
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get(role_code, "U")
#     count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# # ======================================================
# # 🔵 ENVOI OTP EMAIL
# # ======================================================
# @require_POST
# def send_email_otp_view(request):
#     if not EMAIL_VERIFICATION_ENABLED:
#         return JsonResponse({"ok": True, "skipped": True})

#     try:
#         data = json.loads(request.body)
#         email = data.get("email")
#     except json.JSONDecodeError:
#         return JsonResponse({"ok": False, "error": "Requête invalide"})

#     if not email:
#         return JsonResponse({"ok": False, "error": _("Email manquant")})

#     last_sent = request.session.get("otp_last_sent_at_email")
#     if last_sent and (now().timestamp() - last_sent) < 60:
#         return JsonResponse({"ok": False, "error": _("Veuillez patienter avant de redemander un code.")})

#     try:
#         with transaction.atomic():
#             EmailOTP.objects.filter(email=email, is_verified=False).update(is_expired=True)
#             otp = create_email_otp(email)
#             request.session["otp_email"] = email
#             request.session["otp_last_sent_at_email"] = now().timestamp()
#     except Exception as e:
#         return JsonResponse({"ok": False, "error": str(e)})

#     return JsonResponse({"ok": True})


# # ======================================================
# # 🔵 VALIDATION OTP EMAIL
# # ======================================================
# @require_POST
# def verify_email_otp_view(request):
#     if not EMAIL_VERIFICATION_ENABLED:
#         return JsonResponse({"ok": True, "skipped": True})

#     try:
#         data = json.loads(request.body)
#         email = data.get("email")
#         code = data.get("code")
#     except json.JSONDecodeError:
#         return JsonResponse({"ok": False, "error": "Requête invalide"})

#     if not email or not code:
#         return JsonResponse({"ok": False, "error": _("Données manquantes")})

#     if request.session.get("otp_email") != email:
#         return JsonResponse({"ok": False, "error": _("Tentative non autorisée")})

#     try:
#         otp = EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         return JsonResponse({"ok": False, "error": _("Code invalide")})

#     if otp.is_expired_now():
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         return JsonResponse({"ok": False, "error": _("Code expiré")})

#     if otp.code != code:
#         otp.register_attempt()
#         if otp.attempts >= 3:
#             return JsonResponse({"ok": False, "error": _("Trop de tentatives. Veuillez redemander un nouveau code.")})
#         return JsonResponse({"ok": False, "error": _("Code incorrect")})

#     otp.verify()
#     mark_profile_email_verified(email)
#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)

#     return JsonResponse({"ok": True})


# # ======================================================
# # 🔵 INSCRIPTION SOCIALE
# # ======================================================
# def social_register_view(request):
#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # ----------------------------
#                     # 1️⃣ USER
#                     # ----------------------------
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # ----------------------------
#                     # 2️⃣ SOCIAL PROFILE
#                     # ----------------------------
#                     social_profile = profile_form.save(commit=False)
#                     social_profile.user = user

#                     role_code = social_profile.membership_role.code if social_profile.membership_role else None
#                     social_profile.social_registration_code = generate_social_code(role_code)
#                     social_profile.save()

#                     # ----------------------------
#                     # 3️⃣ EMAIL ACTIVATION
#                     # ----------------------------
#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)
#                     activation_url = request.build_absolute_uri(reverse("accounts_users_web:activate", kwargs={"uidb64": uid, "token": token}))

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {"user": user, "activation_url": activation_url, "year": now().year},
#                     )

#                     if settings.DEFAULT_FROM_EMAIL:
#                         send_mail(
#                             subject=_("Activation de votre compte SOGENTIS"),
#                             message=_("Veuillez activer votre compte via le lien reçu."),
#                             from_email=settings.DEFAULT_FROM_EMAIL,
#                             recipient_list=[user.email],
#                             html_message=html_message,
#                         )
#                     else:
#                         user.email_user(
#                             subject=_("Activation de votre compte SOGENTIS"),
#                             message=_("Veuillez activer votre compte via le lien reçu."),
#                             html_message=html_message,
#                         )

#                 messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#                 return redirect("accounts_users_web:login")

#             except IntegrityError:
#                 logger.warning("Email déjà utilisé")
#                 user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#                 messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             except Exception as e:
#                 logger.exception("Erreur inscription sociale : %s", e)
#                 messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#         return render(
#             request,
#             "accounts_users/registration/social_register_form.html",
#             {
#                 "form": user_form,
#                 "profile_form": profile_form,
#                 "excluded_profile_fields": excluded_profile_fields,
#             },
#         )

#     # ----------------------------
#     # GET
#     # ----------------------------
#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )






# # accounts_users/web/views/social/social_registration_view.py

# import logging

# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.conf import settings
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token
# from accounts_users.models.social.social_profile import SocialProfile

# logger = logging.getLogger(__name__)
# User = get_user_model()

# # ======================================================
# # 🔵 GÉNÉRATION DU CODE SOCIAL
# # ======================================================
# def generate_social_code(role_code: str | None) -> str:
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }

#     prefix = prefix_map.get(role_code, "U")

#     count = SocialProfile.objects.filter(
#         membership_role__code=role_code
#     ).count() + 1

#     return f"{prefix}{count:03}"


# # ======================================================
# # 🔵 INSCRIPTION SOCIALE (PUBLIQUE / ADMIN)
# # ======================================================
# def social_register_view(request):
#     """
#     Inscription sociale :
#     - Activation par email (ACTIVE)
#     - OTP téléphone prêt mais désactivé
#     - Génération automatique du code social
#     """

#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # ----------------------------
#                     # 1️⃣ USER
#                     # ----------------------------
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # ----------------------------
#                     # 2️⃣ SOCIAL PROFILE
#                     # ----------------------------
#                     social_profile = profile_form.save(commit=False)
#                     social_profile.user = user

#                     role_code = (
#                         social_profile.membership_role.code
#                         if social_profile.membership_role
#                         else None
#                     )

#                     social_profile.social_registration_code = generate_social_code(
#                         role_code
#                     )
#                     social_profile.save()

#                     # ----------------------------
#                     # 3️⃣ EMAIL ACTIVATION
#                     # ----------------------------
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

#                     # Support send_mail OU email_user
#                     if settings.DEFAULT_FROM_EMAIL:
#                         send_mail(
#                             subject=_("Activation de votre compte SOGENTIS"),
#                             message=_(
#                                 "Veuillez activer votre compte via le lien reçu."
#                             ),
#                             from_email=settings.DEFAULT_FROM_EMAIL,
#                             recipient_list=[user.email],
#                             html_message=html_message,
#                         )
#                     else:
#                         user.email_user(
#                             subject=_("Activation de votre compte SOGENTIS"),
#                             message=_(
#                                 "Veuillez activer votre compte via le lien reçu."
#                             ),
#                             html_message=html_message,
#                         )

#                 messages.success(
#                     request,
#                     _("Un lien d’activation vous a été envoyé par e-mail."),
#                 )
#                 return redirect("accounts_users_web:login")

#             except IntegrityError:
#                 logger.warning("Email déjà utilisé")
#                 user_form.add_error(
#                     "email", _("Un utilisateur avec cet email existe déjà.")
#                 )
#                 messages.error(
#                     request,
#                     _("Un utilisateur avec cet email existe déjà."),
#                 )

#             except Exception as e:
#                 logger.exception("Erreur inscription sociale : %s", e)
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue. Veuillez réessayer."),
#                 )
#         else:
#             messages.error(
#                 request,
#                 _("Merci de corriger les erreurs ci-dessous."),
#             )

#         return render(
#             request,
#             "accounts_users/registration/social_register_form.html",
#             {
#                 "form": user_form,
#                 "profile_form": profile_form,
#                 "excluded_profile_fields": excluded_profile_fields,
#             },
#         )

#     # ----------------------------
#     # GET
#     # ----------------------------
#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()

#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )








# # accounts_users/web/views/social/social_registration_view.py
# import logging

# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def social_register_view(request):
#     """
#     Inscription sociale:
#     - Email activation: ACTIVE
#     - OTP téléphone: prêt, mais désactivé par défaut (PHONE_OTP_ENABLED=False)
#     """

#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     profile_form.save(user=user, commit=True)

#                     uid = urlsafe_base64_encode(force_bytes(user.pk))
#                     token = account_activation_token.make_token(user)

#                     activation_url = request.build_absolute_uri(
#                         reverse("accounts_users_web:activate", kwargs={"uidb64": uid, "token": token})
#                     )

#                     html_message = render_to_string(
#                         "accounts_users/emails/account_activation_email.html",
#                         {"user": user, "activation_url": activation_url, "year": now().year},
#                     )

#                     user.email_user(
#                         subject=_("Activation de votre compte SOGENTIS"),
#                         message=_("Veuillez activer votre compte via le lien reçu."),
#                         html_message=html_message,
#                     )

#                 messages.success(request, _("Un lien d’activation vous a été envoyé par e-mail."))
#                 return redirect("accounts_users_web:login")

#             except IntegrityError:
#                 user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#                 messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#             except Exception as e:
#                 logger.exception("Erreur inscription sociale : %s", e)
#                 messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#         # ✅ Important: render avec forms liés => saisie conservée (sauf mdp/fichiers)
#         return render(
#             request,
#             "accounts_users/registration/social_register_form.html",
#             {"form": user_form, "profile_form": profile_form, "excluded_profile_fields": excluded_profile_fields},
#         )

#     # GET
#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()
#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {"form": user_form, "profile_form": profile_form, "excluded_profile_fields": excluded_profile_fields},
#     )







# # accounts_users/web/views/social/social_registration_view.py

# import logging

# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.db import IntegrityError, transaction
# from django.shortcuts import redirect
# from django.template.loader import render_to_string
# from django.urls import reverse_lazy
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _
# from django.views.generic.edit import FormView

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# class SocialRegisterView(FormView):
#     """
#     Inscription sociale (ONG)
#     - OTP email validé dans le formulaire
#     - Redirection uniquement en cas de succès
#     """

#     template_name = "accounts_users/registration/social_register_form.html"
#     form_class = SocialRegistrationForm
#     success_url = reverse_lazy("accounts_users_web:login")

#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     # --------------------------------------------------
#     # CONTEXTE
#     # --------------------------------------------------
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["form"] = context["form"]  # profil social
#         context["user_form"] = context.get("user_form", UserSignupForm())
#         context["excluded_profile_fields"] = self.excluded_profile_fields
#         return context

#     # --------------------------------------------------
#     # GET
#     # --------------------------------------------------
#     def get(self, request, *args, **kwargs):
#         self.user_form = UserSignupForm()
#         return super().get(request, *args, **kwargs)

#     # --------------------------------------------------
#     # POST
#     # --------------------------------------------------
#     def post(self, request, *args, **kwargs):
#         self.user_form = UserSignupForm(request.POST)
#         return super().post(request, *args, **kwargs)

#     # --------------------------------------------------
#     # FORMULAIRE INVALID
#     # --------------------------------------------------
#     def form_invalid(self, form):
#         messages.error(self.request, _("Merci de corriger les erreurs ci-dessous."))
#         return self.render_to_response(
#             self.get_context_data(form=form, user_form=self.user_form)
#         )

#     # --------------------------------------------------
#     # FORMULAIRE VALIDE
#     # --------------------------------------------------
#     def form_valid(self, form):
#         if not self.user_form.is_valid():
#             return self.form_invalid(form)

#         try:
#             with transaction.atomic():
#                 # ---------------------------
#                 # CREATION DE L'UTILISATEUR
#                 # ---------------------------
#                 user = self.user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 # ---------------------------
#                 # CREATION DU PROFIL SOCIAL
#                 # ---------------------------
#                 form.save(user=user)

#                 # ---------------------------
#                 # EMAIL D'ACTIVATION
#                 # ---------------------------
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)

#                 activation_url = self.request.build_absolute_uri(
#                     reverse_lazy(
#                         "accounts_users_web:activate",
#                         kwargs={"uidb64": uid, "token": token},
#                     )
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {
#                         "user": user,
#                         "activation_url": activation_url,
#                         "year": now().year,
#                     },
#                 )

#                 user.email_user(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     html_message=html_message,
#                 )

#             messages.success(
#                 self.request,
#                 _("Un lien d’activation vous a été envoyé par e-mail."),
#             )
#             return redirect(self.success_url)

#         except IntegrityError:
#             self.user_form.add_error(
#                 "email", _("Un utilisateur avec cet email existe déjà.")
#             )
#             return self.form_invalid(form)

#         except Exception as e:
#             logger.exception("Erreur inscription sociale : %s", e)
#             messages.error(
#                 self.request, _("Une erreur est survenue. Veuillez réessayer.")
#             )
#             return self.form_invalid(form)




# # # accounts_users/web/views/social/social_registration_view.py-good

# import logging

# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.db import IntegrityError, transaction
# from django.shortcuts import redirect
# from django.template.loader import render_to_string
# from django.urls import reverse_lazy
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _
# from django.views.generic.edit import FormView

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# class SocialRegisterView(FormView):
#     """
#     Inscription sociale (ONG)
#     - OTP validé dans le formulaire
#     - redirect uniquement en cas de succès
#     """

#     template_name = "accounts_users/registration/social_register_form.html"
#     form_class = SocialRegistrationForm
#     success_url = reverse_lazy("accounts_users_web:login")

#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     # --------------------------------------------------
#     # CONTEXT
#     # --------------------------------------------------
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["form"] = context["form"]  # profile_form
#         context["user_form"] = context.get("user_form", UserSignupForm())
#         context["excluded_profile_fields"] = self.excluded_profile_fields
#         return context

#     # --------------------------------------------------
#     # GET
#     # --------------------------------------------------
#     def get(self, request, *args, **kwargs):
#         self.user_form = UserSignupForm()
#         return super().get(request, *args, **kwargs)

#     # --------------------------------------------------
#     # POST
#     # --------------------------------------------------
#     def post(self, request, *args, **kwargs):
#         self.user_form = UserSignupForm(request.POST)
#         return super().post(request, *args, **kwargs)

#     # --------------------------------------------------
#     # FORM INVALID
#     # --------------------------------------------------
#     def form_invalid(self, form):
#         messages.error(self.request, _("Merci de corriger les erreurs ci-dessous."))
#         return self.render_to_response(
#             self.get_context_data(form=form, user_form=self.user_form)
#         )

#     # --------------------------------------------------
#     # FORM VALID
#     # --------------------------------------------------
#     def form_valid(self, form):
#         if not self.user_form.is_valid():
#             return self.form_invalid(form)

#         try:
#             with transaction.atomic():
#                 # USER
#                 user = self.user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 # PROFILE (OTP déjà validé dans le form)
#                 form.save(user=user)

#                 # EMAIL activation
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)

#                 activation_url = self.request.build_absolute_uri(
#                     reverse_lazy(
#                         "accounts_users_web:activate",
#                         kwargs={"uidb64": uid, "token": token},
#                     )
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {
#                         "user": user,
#                         "activation_url": activation_url,
#                         "year": now().year,
#                     },
#                 )

#                 user.email_user(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     html_message=html_message,
#                 )

#             messages.success(
#                 self.request,
#                 _("Un lien d’activation vous a été envoyé par e-mail."),
#             )
#             return redirect(self.success_url)

#         except IntegrityError:
#             self.user_form.add_error(
#                 "email", _("Un utilisateur avec cet email existe déjà.")
#             )
#             return self.form_invalid(form)

#         except Exception as e:
#             logger.exception("Erreur inscription sociale : %s", e)
#             messages.error(
#                 self.request, _("Une erreur est survenue. Veuillez réessayer.")
#             )
#             return self.form_invalid(form)




# # accounts_users/web/views/social/social_registration_view.py-good
# import logging

# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.db import IntegrityError, transaction
# from django.shortcuts import render, redirect
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.phone_otp import PhoneOTP
# from accounts_users.tokens import account_activation_token

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def social_register_view(request):
#     """
#     Vue d'inscription sociale (ONG) avec vérification OTP téléphone.
#     - ✅ En cas d'erreur: render (on conserve la saisie)
#     - ✅ Redirect uniquement en cas de succès
#     """

#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             phone = profile_form.cleaned_data.get("phone_number")

#             # ✅ OTP obligatoire : PAS de redirect, on ré-affiche le form rempli
#             if not PhoneOTP.objects.filter(phone=phone, is_verified=True).exists():
#                 # idéalement on met l'erreur sur le champ téléphone
#                 profile_form.add_error(
#                     "phone_number",
#                     _("Veuillez vérifier votre numéro de téléphone avant de continuer.")
#                 )
#                 messages.error(request, _("Veuillez vérifier votre numéro de téléphone avant de continuer."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_signup.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#             try:
#                 with transaction.atomic():
#                     # 1) USER
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # 2) PROFILE SOCIAL
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
#                 # ✅ mieux: associer l’erreur au champ email pour que l’utilisateur voie où corriger
#                 user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#                 messages.error(request, _("Un utilisateur avec cet email existe déjà."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_register_form.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#             except Exception as e:
#                 logger.exception("Erreur inscription sociale : %s", e)
#                 messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
#                 return render(
#                     request,
#                     "accounts_users/registration/social_register_form.html",
#                     {
#                         "form": user_form,
#                         "profile_form": profile_form,
#                         "excluded_profile_fields": excluded_profile_fields,
#                     },
#                 )

#         # forms invalides: on ré-affiche avec les données conservées
#         messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#         return render(
#             request,
#             "accounts_users/registration/social_signup.html",
#             {
#                 "form": user_form,
#                 "profile_form": profile_form,
#                 "excluded_profile_fields": excluded_profile_fields,
#             },
#         )

#     # GET
#     user_form = UserSignupForm()
#     profile_form = SocialRegistrationForm()
#     return render(
#         request,
#         "accounts_users/registration/social_register_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#         },
#     )






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
# from accounts_users.models.phone_otp import PhoneOTP

# logger = logging.getLogger(__name__)
# User = get_user_model()


# def social_register_view(request):
#     """
#     Vue d'inscription sociale (ONG) avec vérification OTP téléphone.
#     """

#     excluded_profile_fields = ["terms", "phone_number", "profile_picture", "judicial_record"]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             phone = profile_form.cleaned_data.get("phone_number")

#             # Vérification OTP obligatoire
#             if not PhoneOTP.objects.filter(phone=phone, is_verified=True).exists():
#                 messages.error(
#                     request,
#                     _("Veuillez vérifier votre numéro de téléphone avant de continuer.")
#                 )
#                 return redirect("accounts_users_web:social_register")

#             try:
#                 with transaction.atomic():
#                     # 1) USER
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # 2) PROFILE SOCIAL
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
