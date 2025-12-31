# /web/views/economic/registration_economic.py
import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.db import transaction

# ======================================================
# FORMULAIRES
# ======================================================

# Auth (COMMUN)
from accounts_users.forms.signup_forms import UserSignupForm

# Profil utilisateur économique (CENTRAL)
from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm

# Profils économiques spécialisés
from accounts_users.forms.economic.economic_signup_forms import (
    ClientSignupForm,
    VendorSignupForm,
    CompanySignupForm,
)

# ======================================================
# MODÈLES
# ======================================================
from accounts_users.models.user_role import EconomicRole
from accounts_users.models.users_economic_profile import UserEconomicProfile

from accounts_users.models.economic.client_profile import ClientProfile
from accounts_users.models.economic.vendor_profile import VendorProfile
from accounts_users.models.economic.company_profile import CompanyProfile

logger = logging.getLogger(__name__)

# ======================================================
# CONFIGURATION
# ======================================================

ECONOMIC_REGISTRATION_MAP = {
    "client": {
        "label": _("Client"),
        "role": EconomicRole.CLIENT,
        "form": ClientSignupForm,
        "model": ClientProfile,
        "requires_validation": False,
    },
    "vendor": {
        "label": _("Vendeur"),
        "role": EconomicRole.VENDOR,
        "form": VendorSignupForm,
        "model": VendorProfile,
        "requires_validation": True,
    },
    "b2b": {
        "label": _("Entreprise"),
        "role": EconomicRole.B2B,
        "form": CompanySignupForm,
        "model": CompanyProfile,
        "requires_validation": True,
    },
}

# ======================================================
# CHOIX DU TYPE
# ======================================================

def register_economic_choice_view(request):
    return render(
        request,
        "accounts_users/registration/register_economic_choice.html",
        {
            "auth_pole": "economic",
            "choices": ECONOMIC_REGISTRATION_MAP,
        },
    )

# ======================================================
# INSCRIPTION ÉCONOMIQUE
# ======================================================

@require_http_methods(["GET", "POST"])
def register_economic_view(request):
    economic_type = (request.GET.get("type") or "").strip().lower()

    if economic_type not in ECONOMIC_REGISTRATION_MAP:
        messages.error(request, _("Type de compte économique invalide."))
        return redirect("accounts_users_web:register_economic_choice")

    config = ECONOMIC_REGISTRATION_MAP[economic_type]

    # -----------------------------
    # FORMULAIRES
    # -----------------------------
    user_form = UserSignupForm(request.POST or None)
    profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
    economic_form = config["form"](request.POST or None, request.FILES or None)

    # -----------------------------
    # POST
    # -----------------------------
    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
            try:
                with transaction.atomic():
                    # 1️⃣ UTILISATEUR
                    user = user_form.save(commit=False)
                    user.is_active = not config["requires_validation"]
                    user.save()

                    # 2️⃣ PROFIL UTILISATEUR CENTRAL (économique)
                    profile: UserEconomicProfile = profile_form.save(commit=False)
                    profile.user = user
                    profile.economic_role = config["role"]
                    profile.save()  # génère le code économique si implémenté dans save()

                    # 3️⃣ PROFIL ÉCONOMIQUE SPÉCIALISÉ
                    economic_profile = economic_form.save(commit=False)
                    economic_profile.profile = profile
                    economic_profile.save()

            except Exception:
                logger.exception("Erreur création compte économique (type=%s)", economic_type)
                messages.error(request, _("Une erreur est survenue lors de la création du compte."))
                return redirect("accounts_users_web:register_economic_choice")

            # -----------------------------
            # FEEDBACK
            # -----------------------------
            if config["requires_validation"]:
                messages.success(
                    request,
                    _("Votre compte a été créé et sera activé après validation."),
                )
            else:
                messages.success(request, _("Votre compte a été créé avec succès."))

            return redirect("accounts_users_web:login")

        messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

    return render(
        request,
        "accounts_users/registration/register_economic_form.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "economic_form": economic_form,
            "economic_type": economic_type,
            "auth_pole": "economic",
        },
    )






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
