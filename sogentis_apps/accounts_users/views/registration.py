# accounts_users/views/registration.py
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from accounts_users.tokens import account_activation_token
from accounts_users.forms.signup_forms import UserSignupForm
from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
from accounts_users.models.users_economic_profile import UserProfile



# ======================================================
# CHOIX DU TYPE DE COMPTE
# ======================================================
def registration_choice_view(request):
    return render(
        request,
        "accounts_users/registration/choice.html",
        {
            "page_title": _("Créer un compte"),
            "registration_social_url": reverse("accounts_users:web:registration:social_register"),
            "registration_economic_url": reverse("accounts_users:web:registration:register_economic"),
        },
    )
    


# ======================================================
# GÉNÉRATION CODE SOCIAL
# ======================================================
def generate_registration_code(role_code):
    prefix = {
        "MEMBER": "M",
        "VOLUNTEER": "V",
        "SPONSOR": "D",
        "INSTITUTION": "I",
    }.get(role_code, "U")

    count = UserProfile.objects.count() + 1
    return f"{prefix}{count:04}"


# ======================================================
# CRÉATION COMPTE + PROFIL SOCIAL (ONG)
# ======================================================
def create_social_user_and_profile(user_data, social_data, files=None):
    """
    Création complète :
    - utilisateur inactif
    - profil social
    - code d’inscription social
    - uid + token activation
    """

    user_form = UserSignupForm(user_data)
    social_form = SocialRegistrationForm(social_data, files)

    if not (user_form.is_valid() and social_form.is_valid()):
        return None, None, user_form, social_form

    # 1️⃣ Utilisateur
    user = user_form.save(commit=False)
    user.is_active = False
    user.set_password(user_form.cleaned_data["password"])
    user.save()

    # 2️⃣ Profil social
    social_profile = social_form.save(commit=False)
    social_profile.user = user

    role_code = (
        social_profile.membership_role.code
        if social_profile.membership_role
        else None
    )
    social_profile.membership_code = generate_registration_code(role_code)
    social_profile.save()

    # 3️⃣ Activation
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    return user, social_profile, uid, token










# # accounts_users/views/registration.py
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.tokens import account_activation_token
# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes

# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _


# def registration_choice_view(request):
#     """
#     Choix du type de compte à créer (registration)
#     """
#     return render(
#         request,
#         "accounts_users/registration/choice.html",
#         {
#             "page_title": _("Créer un compte"),
#             "registration_social_url": reverse("accounts_users_web:social_register"),
#             # "registration_social_url": reverse("accounts_users_web:register_social"),
#             "registration_economic_url": reverse("accounts_users_web:register_economic"),
#         }
#     )

# def generate_registration_code(role_code):
#     prefix = {
#         'MEMBER': 'M',
#         'VOLUNTEER': 'V',
#         'SPONSOR': 'D',
#         'INSTITUTION': 'I',
#     }.get(role_code, 'U')

#     count = UserProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# def create_user_and_profile(user_data, profile_data, files=None):
#     """
#     Logique PURE : pas de render(), pas de messages, pas de mails.
#     - Crée user inactif
#     - Crée profil
#     - Génère registration_code
#     - Génère uid/token pour email d’activation
#     """
#     user_form = UserSignupForm(user_data)
#     profile_form = UserProfileForm(profile_data, files)

#     if not (user_form.is_valid() and profile_form.is_valid()):
#         return None, None, user_form, profile_form

#     # Création utilisateur
#     user = user_form.save(commit=False)
#     user.set_password(user_form.cleaned_data['password'])
#     user.is_active = False
#     user.save()

#     # Création profil
#     profile = profile_form.save(commit=False)
#     profile.user = user

#     role_code = profile.membership_role.code if profile.membership_role else None
#     profile.registration_code = generate_registration_code(role_code)

#     profile.save()

#     # Génération uid + token pour activation
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     return user, profile, uid, token








# # accounts_users/views/registration.py
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.contrib.sites.shortcuts import get_current_site
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.contrib.auth import login

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.tokens import account_activation_token


# def generate_registration_code(role_code):
#     prefix = {
#         'MEMBER': 'M',
#         'VOLUNTEER': 'V',
#         'SPONSOR': 'D',
#         'INSTITUTION': 'I',
#     }.get(role_code, 'U')

#     count = UserProfile.objects.filter(membership_role__code=role_code).count() + 1
#     return f"{prefix}{count:03}"


# def web_signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # Création de l'utilisateur (désactivé jusqu'à confirmation)
#             user = user_form.save(commit=False)
#             user.is_active = False
#             user.save()

#             # Création du profil utilisateur avec code d’inscription
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             role_code = profile.membership_role.code if profile.membership_role else None
#             profile.registration_code = generate_registration_code(role_code)

#             profile.save()

#             # Envoi de l'email d’activation
#             current_site = get_current_site(request)
#             subject = _("Activez votre compte")
#             message = render_to_string('accounts_users/emails/account_activation_email.html', {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token': account_activation_token.make_token(user),
#             })
#             user.email_user(subject, message)

#             messages.success(request, _("Compte créé. Veuillez vérifier votre e-mail pour activer votre compte."))
#             return redirect('accounts_users_web:login')

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileForm()

#     context = {
#         'form': user_form,
#         'profile_form': profile_form,
#     }
#     return render(request, 'accounts_users/registration/signup.html', context)



# # accounts_users/views/registration.py -> 01/07
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import login
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.core.mail import send_mail
# from django.conf import settings

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.tokens import account_activation_token


# def web_signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # Création de l'utilisateur inactif
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password'])
#             user.is_active = False
#             user.save()

#             # Création du profil utilisateur lié
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()

#             # Génération du lien d’activation
#             current_site = get_current_site(request)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             token = account_activation_token.make_token(user)
#             activation_url = reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
#             activation_link = f"http://{current_site.domain}{activation_url}"

#             # Envoi de l'email
#             subject = _("Activation de votre compte")
#             message = _(
#                 f"Bonjour,\n\n"
#                 f"Merci de vous être inscrit sur SOGENTIS.\n"
#                 f"Veuillez cliquer sur le lien ci-dessous pour activer votre compte :\n\n"
#                 f"{activation_link}\n\n"
#                 f"Si vous n'avez pas initié cette inscription, veuillez ignorer ce message."
#             )
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#             messages.success(request, _("Votre compte a été créé. Un lien d'activation vous a été envoyé par email."))
#             return redirect('accounts_users_web:login')
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileForm()

#     context = {
#         'form': user_form,
#         'profile_form': profile_form,
#     }
#     return render(request, 'accounts_users/registration/signup.html', context)







# def web_signup_view(request):
#     if request.method == 'POST':
#         form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if form.is_valid() and profile_form.is_valid():
#             # Création de l'utilisateur
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()

#             # Création du profil utilisateur
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()

#             login(request, user)
#             messages.success(request, _("Inscription réussie. Bienvenue sur SOGENTIS !"))
#             return redirect('dashboard:index')
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#     else:
#         form = UserSignupForm()
#         profile_form = UserProfileForm()

#     context = {
#         'form': form,
#         'profile_form': profile_form,
#     }
#     return render(request, 'accounts_users/registration/signup.html', context)
