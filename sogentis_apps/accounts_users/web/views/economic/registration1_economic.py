# # accounts_users/web/views/economic/registration1_economic.py
# from __future__ import annotations

# import logging

# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# from accounts_users.models.user_role import EconomicRole
# from accounts_users.models.users_economic_profile import UserEconomicProfile
# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile

# from accounts_users.web.views._helpers import build_auth_context, validate_latest_email_otp_or_add_error

# logger = logging.getLogger(__name__)

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": EconomicRole.CLIENT,
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": EconomicRole.VENDOR,
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": EconomicRole.B2B,
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }


# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {**build_auth_context("economic"), "choices": ECONOMIC_REGISTRATION_MAP},
#     )


# def _render_form(request, *, user_form, profile_form, economic_form, economic_type):
#     config = ECONOMIC_REGISTRATION_MAP.get(economic_type)
#     ctx = {
#         "user_form": user_form,
#         "profile_form": profile_form,
#         "economic_form": economic_form,
#         "economic_type": economic_type,
#         "economic_config": config,
#         **build_auth_context("economic"),
#     }
#     return render(request, "accounts_users/registration/register_economic_form.html", ctx)


# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     economic_type = (request.GET.get("type") or "").strip().lower()

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users:web:registration:choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
#             email = (user_form.cleaned_data.get("email") or "").strip().lower()
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             if not validate_latest_email_otp_or_add_error(
#                 request,
#                 email=email,
#                 otp_code=otp_code,
#                 form=user_form,
#                 field_name="email_otp_code",
#             ):
#                 messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             try:
#                 with transaction.atomic():
#                     user = user_form.save(commit=False)
#                     # économique: compte utilisable directement (ta logique actuelle)
#                     user.is_active = True
#                     user.save()

#                     profile: UserEconomicProfile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]

#                     if config["requires_validation"]:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = False
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "PENDING"
#                     else:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = True
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "APPROVED"

#                     profile.save()

#                     econ_profile = economic_form.save(commit=False)
#                     econ_profile.profile = profile
#                     econ_profile.save()

#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 # return redirect("accounts_users:web:register_economic_choice")
#                 return redirect("accounts_users:web:registration:choice") 


#             if config["requires_validation"]:
#                 messages.success(request, _("Votre compte a été créé. Activation après validation."))
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             return redirect("accounts_users:web:login_economic")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         economic_form=economic_form,
#         economic_type=economic_type,
#     )






# # accounts_users/web/views/economic/registration_economic.py/ok-12-01-2026
# import logging

# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import ClientSignupForm, VendorSignupForm, CompanySignupForm

# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.user_role import EconomicRole
# from accounts_users.models.users_economic_profile import UserEconomicProfile
# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile

# logger = logging.getLogger(__name__)

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": EconomicRole.CLIENT,
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": EconomicRole.VENDOR,
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": EconomicRole.B2B,
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }


# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {"auth_pole": "economic", "login_context": "economic", "choices": ECONOMIC_REGISTRATION_MAP},
#     )


# def _render_form(request, *, user_form, profile_form, economic_form, economic_type):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#             "login_context": "economic",
#         },
#     )


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
#         user_form.add_error("email_otp_code", _("Code OTP incorrect."))
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


# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     economic_type = (request.GET.get("type") or "").strip().lower()

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
#             email = (user_form.cleaned_data.get("email") or "").strip().lower()
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             if not _validate_email_otp(request, email=email, otp_code=otp_code, user_form=user_form):
#                 messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             try:
#                 with transaction.atomic():
#                     user = user_form.save(commit=False)
#                     user.is_active = True
#                     user.save()

#                     profile: UserEconomicProfile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]

#                     if config["requires_validation"]:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = False
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "PENDING"
#                     else:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = True
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "APPROVED"

#                     profile.save()

#                     econ_profile = economic_form.save(commit=False)
#                     econ_profile.profile = profile
#                     econ_profile.save()

#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 return redirect("accounts_users_web:register_economic_choice")

#             if config["requires_validation"]:
#                 messages.success(request, _("Votre compte a été créé. Activation après validation."))
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             return redirect("accounts_users_web:login_economic")  # ✅ BG économique garanti

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         economic_form=economic_form,
#         economic_type=economic_type,
#     )







# # accounts_users/web/views/economic/registration_economic.py
# import logging

# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.user_role import EconomicRole
# from accounts_users.models.users_economic_profile import UserEconomicProfile

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile


# logger = logging.getLogger(__name__)


# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": EconomicRole.CLIENT,
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": EconomicRole.VENDOR,
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": EconomicRole.B2B,
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }


# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )


# def _render_form(request, *, user_form, profile_form, economic_form, economic_type):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )


# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     economic_type = (request.GET.get("type") or "").strip().lower()

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():

#             email = (user_form.cleaned_data.get("email") or "").strip().lower()
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             # -----------------------------
#             # 0) VALIDATION OTP EMAIL EN BASE
#             # -----------------------------
#             # (optionnel) sécurité session: si présent, doit matcher
#             sess_email = request.session.get("otp_email")
#             if sess_email and sess_email != email:
#                 user_form.add_error("email_otp_code", _("Tentative non autorisée."))
#                 messages.error(request, _("Tentative non autorisée."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             try:
#                 otp = EmailOTP.objects.filter(
#                     email=email,
#                     is_verified=False,
#                     is_expired=False,
#                 ).latest("created_at")
#             except EmailOTP.DoesNotExist:
#                 user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#                 messages.error(request, _("Le code OTP est invalide ou expiré."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             if otp.is_expired_now():
#                 otp.is_expired = True
#                 otp.save(update_fields=["is_expired"])
#                 user_form.add_error("email_otp_code", _("Le code OTP est expiré."))
#                 messages.error(request, _("Le code OTP est expiré."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             if otp.code != otp_code:
#                 otp.register_attempt()
#                 user_form.add_error("email_otp_code", _("Code OTP incorrect."))
#                 messages.error(request, _("Code OTP incorrect."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             # OK -> vérifie OTP (sets verified_at)
#             try:
#                 otp.verify()
#             except Exception:
#                 user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#                 messages.error(request, _("Le code OTP est invalide ou expiré."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             # Nettoyage session OTP
#             request.session.pop("otp_email", None)
#             request.session.pop("otp_last_sent_at_email", None)
#             request.session.modified = True

#             # -----------------------------
#             # 1) CRÉATION UTILISATEUR + PROFILS
#             # -----------------------------
#             try:
#                 with transaction.atomic():
#                     # 1) USER (email vérifié via OTP)
#                     user = user_form.save(commit=False)
#                     user.is_active = True
#                     user.save()

#                     # 2) PROFIL CENTRAL ECONOMIQUE
#                     profile: UserEconomicProfile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]

#                     if config["requires_validation"]:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = False
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "PENDING"
#                     else:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = True
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "APPROVED"

#                     profile.save()

#                     # 3) PROFIL SPÉCIALISÉ
#                     econ_profile = economic_form.save(commit=False)
#                     econ_profile.profile = profile
#                     econ_profile.save()

#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 return redirect("accounts_users_web:register_economic_choice")

#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé. Certaines fonctionnalités seront disponibles après validation."),
#                 )
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         economic_form=economic_form,
#         economic_type=economic_type,
#     )






# # accounts_users/web/views/economic/registration_economic.py
# import logging

# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# from accounts_users.models.user_role import EconomicRole
# from accounts_users.models.users_economic_profile import UserEconomicProfile

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile

# from accounts_users.services.email_otp_service import EmailOTP

# logger = logging.getLogger(__name__)


# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": EconomicRole.CLIENT,
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": EconomicRole.VENDOR,
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": EconomicRole.B2B,
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }


# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )


# def _render_form(request, *, user_form, profile_form, economic_form, economic_type):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )


# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     economic_type = (request.GET.get("type") or "").strip().lower()

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():

#             email = user_form.cleaned_data.get("email")
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             # -----------------------------
#             # VALIDATION OTP EMAIL EN BASE
#             # -----------------------------
#             try:
#                 otp_entry = EmailOTP.objects.get(
#                     email=email,
#                     code=otp_code,
#                     is_verified=False,
#                     is_expired=False,
#                 )
#             except EmailOTP.DoesNotExist:
#                 user_form.add_error("email_otp_code", _("Le code OTP est invalide ou expiré."))
#                 messages.error(request, _("Le code OTP est invalide ou expiré."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             otp_entry.is_verified = True
#             otp_entry.save(update_fields=["is_verified"])

#             # -----------------------------
#             # CRÉATION UTILISATEUR + PROFILS
#             # -----------------------------
#             try:
#                 with transaction.atomic():
#                     # 1) USER (email déjà vérifié via OTP)
#                     user = user_form.save(commit=False)
#                     user.is_active = True
#                     user.save()

#                     # 2) PROFIL CENTRAL ECONOMIQUE
#                     profile: UserEconomicProfile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]

#                     if config["requires_validation"]:
#                         if hasattr(profile, "is_validated"):
#                             setattr(profile, "is_validated", False)
#                         if hasattr(profile, "validation_status"):
#                             setattr(profile, "validation_status", "PENDING")
#                     else:
#                         if hasattr(profile, "is_validated"):
#                             setattr(profile, "is_validated", True)
#                         if hasattr(profile, "validation_status"):
#                             setattr(profile, "validation_status", "APPROVED")

#                     profile.save()

#                     # 3) PROFIL SPECIALISE
#                     econ_profile = economic_form.save(commit=False)
#                     econ_profile.profile = profile
#                     econ_profile.save()

#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 return redirect("accounts_users_web:register_economic_choice")

#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé. Certaines fonctionnalités seront disponibles après validation."),
#                 )
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         economic_form=economic_form,
#         economic_type=economic_type,
#     )




# # /web/views/economic/registration_economic.py
# import logging

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods
# from django.db import transaction

# # ======================================================
# # FORMULAIRES
# # ======================================================

# # Auth (COMMUN)
# from accounts_users.forms.signup_forms import UserSignupForm

# # Profil utilisateur économique (CENTRAL)
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm

# # Profils économiques spécialisés
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# # ======================================================
# # MODÈLES
# # ======================================================
# from accounts_users.models.user_role import EconomicRole
# from accounts_users.models.users_economic_profile import UserEconomicProfile

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile

# logger = logging.getLogger(__name__)

# # ======================================================
# # CONFIGURATION
# # ======================================================

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": EconomicRole.CLIENT,
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": EconomicRole.VENDOR,
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": EconomicRole.B2B,
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }

# # ======================================================
# # CHOIX DU TYPE
# # ======================================================

# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )

# # ======================================================
# # INSCRIPTION ÉCONOMIQUE
# # ======================================================

# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     economic_type = (request.GET.get("type") or "").strip().lower()

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     # -----------------------------
#     # FORMULAIRES
#     # -----------------------------
#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     # -----------------------------
#     # POST
#     # -----------------------------
#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # 1️⃣ UTILISATEUR
#                     user = user_form.save(commit=False)
#                     user.is_active = not config["requires_validation"]
#                     user.save()

#                     # 2️⃣ PROFIL UTILISATEUR CENTRAL (économique)
#                     profile: UserEconomicProfile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]
#                     profile.save()  # génère le code économique si implémenté dans save()

#                     # 3️⃣ PROFIL ÉCONOMIQUE SPÉCIALISÉ
#                     economic_profile = economic_form.save(commit=False)
#                     economic_profile.profile = profile
#                     economic_profile.save()

#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 return redirect("accounts_users_web:register_economic_choice")

#             # -----------------------------
#             # FEEDBACK
#             # -----------------------------
#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé et sera activé après validation."),
#                 )
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )






# # /web/views/economic/registration_economic.py 30/12/2025
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods
# from django.db import transaction

# # ======================================================
# # FORMULAIRES
# # ======================================================

# # Auth (COMMUN)
# from accounts_users.forms.signup_forms import UserSignupForm

# # Profil utilisateur économique (CENTRAL)
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm

# # Profils économiques spécialisés
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# # ======================================================
# # MODÈLES
# # ======================================================

# from accounts_users.models.users_economic_profile import EconomicRole
# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile

# # ======================================================
# # CONFIGURATION
# # ======================================================

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": EconomicRole.CLIENT,
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": EconomicRole.VENDOR,
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": EconomicRole.B2B,
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }

# # ======================================================
# # CHOIX DU TYPE
# # ======================================================

# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )

# # ======================================================
# # INSCRIPTION ÉCONOMIQUE
# # ======================================================

# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):

#     economic_type = (request.GET.get("type") or "").lower()

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     # -----------------------------
#     # FORMULAIRES
#     # -----------------------------
#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(
#         request.POST or None,
#         request.FILES or None,
#     )
#     economic_form = config["form"](
#         request.POST or None,
#         request.FILES or None,
#     )

#     # -----------------------------
#     # POST
#     # -----------------------------
#     if request.method == "POST":

#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():

#             try:
#                 with transaction.atomic():

#                     # 1️⃣ UTILISATEUR
#                     user = user_form.save(commit=False)
#                     user.is_active = not config["requires_validation"]
#                     user.save()

#                     # 2️⃣ PROFIL UTILISATEUR CENTRAL
#                     profile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]
#                     profile.save()

#                     # 3️⃣ PROFIL ÉCONOMIQUE SPÉCIALISÉ
#                     economic_profile = economic_form.save(commit=False)
#                     economic_profile.profile = profile
#                     economic_profile.save()

#             except Exception:
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue lors de la création du compte.")
#                 )
#                 return redirect("accounts_users_web:register_economic_choice")

#             # -----------------------------
#             # FEEDBACK
#             # -----------------------------
#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé et sera activé après validation."),
#                 )
#             else:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé avec succès."),
#                 )

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )









# # accounts_users/web/views/registration_economic.py
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods
# from django.db import transaction

# # ======================================================
# # FORMULAIRES
# # ======================================================

# # User (auth)
# from accounts_users.forms.social.signup_social_forms import UserSignupForm

# # Profil utilisateur (VERSION ÉCONOMIQUE)
# from accounts_users.forms.economic.profile_economic_forms import UserProfileEconomicForm

# # Profils économiques spécialisés
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# # ======================================================
# # MODÈLES ÉCONOMIQUES
# # ======================================================

# from accounts_users.models.economic import (
#     ClientProfile,
#     VendorProfile,
#     CompanyProfile,
# )

# # ======================================================
# # CONFIGURATION CENTRALE DES INSCRIPTIONS ÉCONOMIQUES
# # ======================================================

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": "CLIENT",
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": "VENDOR",
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": "B2B",
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }

# # ======================================================
# # 1️⃣ CHOIX DU TYPE D’INSCRIPTION ÉCONOMIQUE
# # ======================================================

# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )

# # ======================================================
# # 2️⃣ INSCRIPTION ÉCONOMIQUE (CLIENT / VENDEUR / B2B)
# # ======================================================

# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     """
#     Inscription économique :
#     - Client (B2C)
#     - Vendeur
#     - Entreprise (B2B)

#     ⚠️ L’adhésion sociale est FACULTATIVE ici.
#     """

#     economic_type = request.GET.get("type")

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     # ==================================================
#     # FORMULAIRES
#     # ==================================================

#     user_form = UserSignupForm(request.POST or None)

#     profile_form = UserProfileEconomicForm(
#         request.POST or None,
#         request.FILES or None,
#     )

#     economic_form = config["form"](
#         request.POST or None,
#         request.FILES or None,
#     )

#     # ==================================================
#     # TRAITEMENT POST
#     # ==================================================

#     if request.method == "POST":

#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():

#             try:
#                 with transaction.atomic():

#                     # ------------------------------
#                     # 1️⃣ UTILISATEUR
#                     # ------------------------------
#                     user = user_form.save(commit=False)
#                     user.is_active = not config["requires_validation"]
#                     user.save()

#                     # ------------------------------
#                     # 2️⃣ PROFIL UTILISATEUR CENTRAL
#                     # ------------------------------
#                     profile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]
#                     profile.save()

#                     # ------------------------------
#                     # 3️⃣ PROFIL ÉCONOMIQUE SPÉCIALISÉ
#                     # ------------------------------
#                     economic_profile = economic_form.save(commit=False)
#                     economic_profile.profile = profile
#                     economic_profile.save()

#             except Exception:
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue lors de la création du compte.")
#                 )
#                 return redirect("accounts_users_web:register_economic_choice")

#             # ------------------------------
#             # FEEDBACK UTILISATEUR
#             # ------------------------------
#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé et sera activé après validation."),
#                 )
#             else:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé avec succès."),
#                 )

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     # ==================================================
#     # RENDU TEMPLATE
#     # ==================================================

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )





# # accounts_users/web/views/registration_economic.py
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods
# from django.db import transaction

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.forms.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# from accounts_users.models.economic import (
#     ClientProfile,
#     VendorProfile,
#     CompanyProfile,
# )

# # ======================================================
# # CONFIGURATION CENTRALE DES INSCRIPTIONS ÉCONOMIQUES
# # ======================================================

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": "CLIENT",
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": "VENDOR",
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": "B2B",
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }

# # ======================================================
# # 1️⃣ CHOIX DU TYPE D’INSCRIPTION ÉCONOMIQUE
# # ======================================================

# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )

# # ======================================================
# # 2️⃣ INSCRIPTION ÉCONOMIQUE (CLIENT / VENDEUR / B2B)
# # ======================================================

# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     """
#     Inscription économique :
#     - client
#     - vendeur
#     - entreprise (B2B)
#     """

#     economic_type = request.GET.get("type")

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     # ---------- Formulaires ----------
#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():

#             try:
#                 with transaction.atomic():

#                     # ---------- USER ----------
#                     user = user_form.save(commit=False)
#                     user.is_active = not config["requires_validation"]
#                     user.save()

#                     # ---------- PROFIL UTILISATEUR ----------
#                     profile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]
#                     profile.save()

#                     # ---------- PROFIL ÉCONOMIQUE SPÉCIALISÉ ----------
#                     economic_profile = economic_form.save(commit=False)
#                     economic_profile.profile = profile
#                     economic_profile.save()

#             except Exception:
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue lors de la création du compte.")
#                 )
#                 return redirect("accounts_users_web:register_economic_choice")

#             # ---------- FEEDBACK ----------
#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé et sera activé après validation."),
#                 )
#             else:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé avec succès."),
#                 )

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )






# # accounts_users/web/views/registration_economic.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.forms.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# from accounts_users.models.economic import (
#     ClientProfile,
#     VendorProfile,
#     CompanyProfile,
# )

# # ======================================================
# # CONFIGURATION CENTRALE DES INSCRIPTIONS ÉCONOMIQUES
# # ======================================================

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": "CLIENT",
#         "form": ClientSignupForm,
#         "model": ClientProfile,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": "VENDOR",
#         "form": VendorSignupForm,
#         "model": VendorProfile,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": "B2B",
#         "form": CompanySignupForm,
#         "model": CompanyProfile,
#         "requires_validation": True,
#     },
# }


# # ======================================================
# # 1️⃣ CHOIX DU TYPE D’INSCRIPTION ÉCONOMIQUE
# # ======================================================

# def register_economic_choice_view(request):
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#             "choices": ECONOMIC_REGISTRATION_MAP,
#         },
#     )


# # ======================================================
# # 2️⃣ INSCRIPTION ÉCONOMIQUE INTELLIGENTE
# # ======================================================

# @require_http_methods(["GET", "POST"])
# def register_economic_view(request):
#     """
#     Inscription économique :
#     - client
#     - vendeur
#     - entreprise (B2B)
#     """

#     economic_type = request.GET.get("type")

#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     # ---------- Formulaires ----------
#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():

#             # ---------- USER ----------
#             user = user_form.save(commit=False)
#             user.is_active = not config["requires_validation"]
#             user.save()

#             # ---------- PROFIL COMMUN ----------
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.economic_role = config["role"]
#             profile.save()

#             # ---------- PROFIL ÉCONOMIQUE SPÉCIALISÉ ----------
#             economic_profile = economic_form.save(commit=False)
#             economic_profile.profile = profile
#             economic_profile.save()

#             # ---------- FEEDBACK ----------
#             if config["requires_validation"]:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé et sera activé après validation."),
#                 )
#             else:
#                 messages.success(
#                     request,
#                     _("Votre compte a été créé avec succès."),
#                 )

#             return redirect("accounts_users_web:login")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )











# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.user_role import EconomicRole


# def register_economic_choice_view(request):
#     """
#     Choix du type d'inscription économique.
#     """
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {
#             "auth_pole": "economic",
#         },
#     )


# def register_economic_view(request):
#     """
#     Inscription économique (client / vendeur / entreprise).
#     """

#     economic_type = request.GET.get("type")

#     ECONOMIC_MAP = {
#         "client": EconomicRole.CLIENT,
#         "vendor": EconomicRole.VENDOR,
#         "b2b": EconomicRole.B2B,
#     }

#     if economic_type not in ECONOMIC_MAP:
#         messages.error(request, _("Type de compte invalide."))
#         return redirect("accounts_users_web:register_economic_choice")

#     form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileForm(request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if form.is_valid() and profile_form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # validation requise
#             user.save()

#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.economic_role = ECONOMIC_MAP[economic_type]
#             profile.membership_role = None  # sécurité : pas de social ici
#             profile.save()

#             messages.success(
#                 request,
#                 _("Votre compte a été créé. Il sera activé après validation."),
#             )
#             return redirect("accounts_users_web:login")

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "form": form,
#             "profile_form": profile_form,
#             "economic_type": economic_type,
#             "auth_pole": "economic",
#         },
#     )











# # # accounts_users/web/views/registration_economic.py
# # from django.shortcuts import render, redirect
# # from django.contrib import messages
# # from django.utils.translation import gettext_lazy as _

# # from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm


# # def register_economic_choice_view(request):
# #     """
# #     Choix du type d'inscription économique.
# #     """
# #     return render(
# #         request,
# #         "accounts_users/registration/register_economic_choice.html",
# #         {"auth_pole": "economic"},
# #     )


# # def register_economic_view(request):
# #     """
# #     Inscription économique (client / vendeur / b2b).
# #     """
# #     economic_type = request.GET.get("type")

# #     if economic_type not in ("client", "vendor", "b2b"):
# #         messages.error(request, _("Type de compte invalide."))
# #         return redirect("accounts_users_web:register_economic_choice")

# #     form = UserSignupForm(request.POST or None)
# #     profile_form = UserProfileForm(request.POST or None, request.FILES or None)

# #     if request.method == "POST":
# #         if form.is_valid() and profile_form.is_valid():
# #             user = form.save(commit=False)
# #             user.is_active = False  # validation requise
# #             user.save()

# #             profile = profile_form.save(commit=False)
# #             profile.user = user
# #             profile.economic_role = economic_type.upper()
# #             # profile.account_type = economic_type  # champ à prévoir
# #             profile.save()

# #             messages.success(
# #                 request,
# #                 _("Votre compte a été créé. Il sera activé après validation."),
# #             )
# #             return redirect("accounts_users_web:login")

# #     return render(
# #         request,
# #         "accounts_users/registration/register_economic_form.html",
# #         {
# #             "form": form,
# #             "profile_form": profile_form,
# #             "economic_type": economic_type,
# #             "auth_pole": "economic",
# #         },
# #     )
