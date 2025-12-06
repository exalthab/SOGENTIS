# accounts_users/web/views/registration_views.py
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail, mail_admins
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now
from datetime import timedelta

from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
from accounts_users.forms.resend_activation_form import ResendActivationEmailForm
from accounts_users.models.user_role import UserRole
from accounts_users.models.users_profile import UserProfile
from accounts_users.tokens import account_activation_token  # ✅ ton token personnalisé

User = get_user_model()

def generate_registration_code(role_code):
    prefix = {
        'MEMBER': 'M',
        'VOLUNTEER': 'V',
        'SPONSOR': 'D',
        'INSTITUTION': 'I',
    }.get(role_code, 'U')
    count = UserProfile.objects.filter(membership_role__code=role_code).count() + 1
    return f"{prefix}{count:03}"

# --- Vue d'inscription ---
def signup_view(request):
    if request.method == 'POST':
        user_form = UserSignupForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.is_active = False
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # Génére code d’inscription basé sur le rôle
            role_code = profile.membership_role.code if profile.membership_role else None
            profile.registration_code = generate_registration_code(role_code)

            # Gestion du rôle d’adhésion
            role_selected = profile_form.cleaned_data.get("role")
            if isinstance(role_selected, str):
                try:
                    role_selected = UserRole.objects.get(role=role_selected)
                except UserRole.DoesNotExist:
                    messages.error(request, _("Le rôle sélectionné n'existe pas."))
                    return render(request, 'accounts_users/registration/signup.html', {
                        'form': user_form,
                        'profile_form': profile_form,
                    })
            if isinstance(role_selected, UserRole):
                profile.role = role_selected

            profile.save()

            # Notifie l’admin d’un nouveau casier judiciaire (si besoin)
            mail_admins(
                subject="📥 Nouveau casier judiciaire soumis",
                message=f"Un nouveau casier judiciaire a été soumis par {user.email}.",
                fail_silently=True,
            )

            # Génération du lien d’activation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_url = request.build_absolute_uri(
                reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
            )
            context = {
                'user': user,
                'activation_url': activation_url,
                'year': now().year
            }
            subject = _("Activation de votre compte SOGENTIS")
            message_txt = _(
                f"Bonjour,\n\nMerci pour votre inscription sur SOGENTIS.\n"
                f"Veuillez activer votre compte via le lien suivant :\n{activation_url}"
            )
            html_message = render_to_string('accounts_users/emails/account_activation_email.html', context)

            send_mail(
                subject=subject,
                message=message_txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, _("Un lien de confirmation vous a été envoyé par e-mail."))
            return redirect('accounts_users_web:login')

        else:
            messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
    else:
        user_form = UserSignupForm()
        profile_form = UserProfileForm()

    return render(request, 'accounts_users/registration/signup.html', {
        'form': user_form,
        'profile_form': profile_form,
    })

# --- Vue d’activation ---
def activate_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        if user.is_active:
            messages.info(request, _("Ce compte est déjà activé."))
        else:
            user.is_active = True
            user.save()
            login(request, user)
            send_mail(
                subject=_("Bienvenue sur SOGENTIS"),
                message=_("Bonjour,\n\nVotre compte a bien été activé.\nBienvenue sur SOGENTIS !"),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, _("Votre compte a été activé avec succès."))
        return redirect('dashboard:index')
    else:
        messages.error(request, _("Le lien d’activation est invalide ou a expiré."))
        return render(request, 'accounts_users/registration/activation_invalid.html')

# --- Réexpédition du lien d'activation ---
def resend_activation_view(request):
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, _("Aucun utilisateur avec cet e-mail."))
                return redirect('accounts_users_web:resend_activation')

            last_sent = request.session.get('last_activation_sent')
            # Contrôle anti-abus : 10 minutes avant nouvel envoi
            if last_sent and now() < last_sent + timedelta(minutes=10):
                messages.warning(request, _("Veuillez patienter avant de redemander un lien."))
                return redirect('accounts_users_web:resend_activation')

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_url = request.build_absolute_uri(
                reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
            )
            context = {
                'user': user,
                'activation_url': activation_url,
                'year': now().year
            }
            subject = _("Nouveau lien d’activation")
            message_txt = _("Bonjour,\n\nVoici un nouveau lien pour activer votre compte :\n") + activation_url
            html_message = render_to_string('accounts_users/emails/account_activation_email.html', context)

            send_mail(
                subject=subject,
                message=message_txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            request.session['last_activation_sent'] = now()
            messages.success(request, _("Un nouveau lien d'activation vous a été envoyé."))
            return redirect('accounts_users_web:login')
    else:
        form = ResendActivationEmailForm()

    return render(request, 'accounts_users/registration/resend_activation.html', {'form': form})




# # accounts_users/web/views/registration_views.py
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.core.mail import send_mail
# from django.core.mail import mail_admins
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext as _
# from django.contrib.auth import get_user_model, login
# from django.conf import settings
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from datetime import timedelta

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.user_role import UserRole
# # from accounts_users.forms.resend_activation_form import ResendActivationForm
# from accounts_users.forms.resend_activation_form import ResendActivationEmailForm



# User = get_user_model()

# # --- Signup View ---
# def signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # 🔐 Création d'un utilisateur inactif
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password'])
#             user.is_active = False
#             user.save()

#             # 📎 Création du profil
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # 🎯 Rôle
#             role_selected = profile_form.cleaned_data.get("role")
#             if isinstance(role_selected, str):
#                 try:
#                     role_selected = UserRole.objects.get(role=role_selected)
#                 except UserRole.DoesNotExist:
#                     messages.error(request, _("Le rôle sélectionné n'existe pas."))
#                     return render(request, 'accounts_users/registration/signup.html', {
#                         'form': user_form,
#                         'profile_form': profile_form,
#                     })
#             if isinstance(role_selected, UserRole):
#                 profile.role = role_selected
#             else:
#                 messages.error(request, _("Le rôle est invalide."))
#                 return render(request, 'accounts_users/registration/signup.html', {
#                     'form': user_form,
#                     'profile_form': profile_form,
#                 })

#             profile.save()
#             # Après profile.save()
#             mail_admins(
#                 subject="📥 Nouveau casier judiciaire soumis",
#                 message=f"Un nouveau casier judiciaire a été soumis par {user.email}. Veuillez le vérifier dans l'admin.",
#                 fail_silently=True,
#             )

#             # 📧 Génération du lien d'activation
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             activation_url = request.build_absolute_uri(
#                 reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
#             )

#             # ✉️ Envoi email HTML
#             context = {
#                 'user': user,
#                 'activation_url': activation_url,
#                 'year': now().year
#             }
#             subject = _("Activation de votre compte SOGENTIS")
#             message_txt = _(
#                 f"Bonjour {user.first_name},\n\n"
#                 f"Merci pour votre inscription sur SOGENTIS.\n"
#                 f"Veuillez activer votre compte via le lien suivant :\n{activation_url}"
#             )
#             html_message = render_to_string('accounts_users/emails/account_activation_email.html', context)

#             send_mail(
#                 subject=subject,
#                 message=message_txt,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 html_message=html_message,
#                 fail_silently=False,
#             )

#             messages.success(request, _("Un lien de confirmation vous a été envoyé par e-mail."))
#             return redirect('accounts_users_web:confirmation_sent')

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileForm()

#     return render(request, 'accounts_users/registration/signup.html', {
#         'form': user_form,
#         'profile_form': profile_form,
#     })


# # --- Activation View ---
# def activate_view(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user and default_token_generator.check_token(user, token):
#         if user.is_active:
#             messages.info(request, _("Ce compte est déjà activé."))
#         else:
#             user.is_active = True
#             user.save()
#             login(request, user)

#             # ✉️ Email de bienvenue
#             subject = _("Bienvenue sur SOGENTIS")
#             message = _(
#                 f"Bonjour {user.first_name},\n\n"
#                 f"Votre compte a bien été activé.\n"
#                 f"Bienvenue sur SOGENTIS !"
#             )
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#             messages.success(request, _("Votre compte a été activé avec succès."))

#         return redirect('dashboard:index')

#     else:
#         messages.error(request, _("Le lien d’activation est invalide ou a expiré."))
#         return render(request, 'accounts_users/registration/activation_invalid.html')


# # --- Resend Activation View ---
# def resend_activation_view(request):
#     if request.method == 'POST':
#         form = ResendActivationEmailForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             user = User.objects.get(email=email)

#             # ✅ Anti-abus : 10 min d'attente
#             last_sent = request.session.get('last_activation_sent')
#             if last_sent and now() < last_sent + timedelta(minutes=10):
#                 messages.warning(request, _("Veuillez patienter avant de redemander un lien."))
#                 return redirect('accounts_users_web:resend_activation')

#             # Génération du lien
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             activation_url = request.build_absolute_uri(
#                 reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
#             )

#             # Envoi e-mail
#             context = {
#                 'user': user,
#                 'activation_url': activation_url,
#                 'year': now().year
#             }
#             subject = _("Nouveau lien d’activation")
#             message_txt = _(
#                 f"Bonjour {user.first_name},\n\n"
#                 f"Voici un nouveau lien pour activer votre compte :\n{activation_url}"
#             )
#             html_message = render_to_string('accounts_users/emails/account_activation_email.html', context)

#             send_mail(
#                 subject=subject,
#                 message=message_txt,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 html_message=html_message,
#                 fail_silently=False,
#             )

#             # Sauvegarde timestamp session
#             request.session['last_activation_sent'] = now()

#             messages.success(request, _("Un nouveau lien d'activation vous a été envoyé."))
#             return redirect('accounts_users_web:login')
#     else:
#         form = ResendActivationEmailForm()

#     return render(request, 'accounts_users/registration/resend_activation.html', {'form': form})






# # accounts_users/web/views/registration_views.py

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.core.mail import send_mail
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext as _
# from django.contrib.auth import get_user_model
# from django.conf import settings
# from django.contrib.auth import login
# from django.template.loader import render_to_string
# from django.utils.timezone import now

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.role import UserRole

# from accounts_users.forms.resend_activation_form import ResendActivationForm


# User = get_user_model()


# def signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # 🔐 Création d'un utilisateur inactif
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password'])
#             user.is_active = False
#             user.save()

#             # 📎 Création du profil
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # 🎯 Gestion du rôle (string ou instance)
#             role_selected = profile_form.cleaned_data.get("role")
#             if isinstance(role_selected, str):
#                 try:
#                     role_instance = UserRole.objects.get(role=role_selected)
#                 except UserRole.DoesNotExist:
#                     messages.error(request, _("Le rôle sélectionné n'existe pas."))
#                     return render(request, 'accounts_users/registration/signup.html', {
#                         'form': user_form,
#                         'profile_form': profile_form,
#                     })
#                 profile.role = role_instance
#             elif isinstance(role_selected, UserRole):
#                 profile.role = role_selected
#             else:
#                 messages.error(request, _("Le rôle est invalide."))
#                 return render(request, 'accounts_users/registration/signup.html', {
#                     'form': user_form,
#                     'profile_form': profile_form,
#                 })

#             profile.save()

#             # 📧 Génération du lien d'activation
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             activation_url = request.build_absolute_uri(
#                 reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
#             )

#             # ✉️ Envoi de l'email de confirmation
#             subject = _("Activation de votre compte SOGENTIS")
#             message = _(
#                 f"Bonjour {user.first_name},\n\n"
#                 f"Merci pour votre inscription sur SOGENTIS.\n\n"
#                 f"Veuillez cliquer sur le lien ci-dessous pour activer votre compte :\n\n"
#                 f"{activation_url}\n\n"
#                 f"Si vous n'avez pas demandé cette inscription, veuillez ignorer cet e-mail."
#             )

#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#             messages.success(request, _("Un lien de confirmation vous a été envoyé par e-mail."))
#             return redirect('accounts_users_web:confirmation_sent')

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))

#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileForm()

#     return render(request, 'accounts_users/registration/signup.html', {
#         'form': user_form,
#         'profile_form': profile_form,
#     })

# def activate_view(request, uidb64, token):
#     try:
#         # Décodage de l'UID base64
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):
#         if user.is_active:
#             messages.info(request, _("Ce compte est déjà activé."))
#         else:
#             user.is_active = True
#             user.save()
#             login(request, user)
#             subject = _("Bienvenue sur SOGENTIS")
#             message = _(
#                 f"Bonjour {user.first_name},\n\n"
#                 f"Votre compte a bien été activé. Vous pouvez désormais accéder à toutes les fonctionnalités de SOGENTIS.\n\n"
#                 f"Merci de votre confiance.\nL'équipe SOGENTIS"
#             )
#             messages.success(request, message)
            
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#         login(request, user)
#         messages.success(request, _("Votre compte a été activé avec succès. Bienvenue sur SOGENTIS !"))
#         return redirect('dashboard:index')  # À adapter selon ta logique de redirection
#     else:
#         messages.error(request, _("Le lien d’activation est invalide ou a expiré."))
#         return render(request, 'accounts_users/registration/activation_invalid.html')


# def resend_activation_view(request):
#     if request.method == 'POST':
#         form = ResendActivationForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             user = User.objects.get(email=email)

#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             activation_url = request.build_absolute_uri(
#                 reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
#             )

#             send_mail(
#                 subject=_("Nouveau lien d’activation"),
#                 message=_(
#                     f"Bonjour {user.first_name},\n\n"
#                     f"Voici un nouveau lien pour activer votre compte :\n{activation_url}"
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#             messages.success(request, _("Un nouveau lien d'activation vous a été envoyé."))
#             return redirect('accounts_users_web:login')
#     else:
#         form = ResendActivationForm()

#     return render(request, 'accounts_users/registration/resend_activation.html', {'form': form})







# # accounts_users/web/views/registration_views.py

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.core.mail import send_mail
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext as _
# from django.contrib.auth import get_user_model
# from django.conf import settings

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.role import UserRole

# User = get_user_model()


# def signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # 🔐 Création de l'utilisateur inactif
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password'])
#             user.is_active = False  # Le compte sera activé après confirmation e-mail
#             user.save()

#             # 📎 Création du profil sans encore l'enregistrer
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # 🎯 Gestion du rôle
#             role_selected = profile_form.cleaned_data.get("role")
#             if isinstance(role_selected, str):
#                 try:
#                     role_instance = UserRole.objects.get(role=role_selected)
#                     profile.role = role_instance
#                 except UserRole.DoesNotExist:
#                     messages.error(request, _("Le rôle sélectionné n'existe pas."))
#                     return render(request, 'accounts_users/registration/signup.html', {
#                         'form': user_form,
#                         'profile_form': profile_form,
#                     })

#             profile.save()

#             # 📧 Envoi de l'e-mail de confirmation
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             activation_url = request.build_absolute_uri(
#                 reverse('accounts_users_web:activate', kwargs={'uidb64': uid, 'token': token})
#             )

#             send_mail(
#                 subject=_("Activation de votre compte SOGENTIS"),
#                 message=_(
#                     f"Bonjour {user.first_name},\n\n"
#                     f"Merci de votre inscription. Veuillez cliquer sur le lien ci-dessous pour activer votre compte :\n"
#                     f"{activation_url}\n\n"
#                     f"Si vous n'avez pas demandé cette inscription, ignorez cet e-mail."
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#             messages.success(request, _("Un lien de confirmation vous a été envoyé par e-mail."))
#             return redirect('accounts_users_web:confirmation_sent')

#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileForm()

#     return render(request, 'accounts_users/registration/signup.html', {
#         'form': user_form,
#         'profile_form': profile_form,
#     })




# # accounts_users/web/views/registration_views.py

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.urls import reverse
# from django.core.mail import send_mail
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext as _
# from django.contrib.auth import login

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.role import UserRole


# def signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # 🔐 Création de l'utilisateur
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password'])
#             user.save()

#             # 📎 Traitement du profil
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()


#             # 🎯 Correction ici : on récupère une instance UserRole depuis le champ sélectionné
#             role_selected = profile_form.cleaned_data.get("role")
#             if isinstance(role_selected, str):
#                 try:
#                     role_instance = UserRole.objects.get(role=role_selected)
#                     profile.role = role_instance
#                 except UserRole.DoesNotExist:
#                     messages.error(request, _("Le rôle sélectionné n'existe pas."))
#                     return render(request, 'accounts_users/registration/signup.html', {
#                         'form': user_form,
#                         'profile_form': profile_form,
#                     })

#             profile.save()

#             login(request, user)
#             messages.success(request, _("Inscription réussie. Bienvenue sur SOGENTIS !"))
#             return redirect('dashboard:index')
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileForm()

#     return render(request, 'accounts_users/registration/signup.html', {
#         'form': user_form,
#         'profile_form': profile_form,
#     })




# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import login

# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm
# from accounts_users.models.users_profile import UserProfile


# def signup_view(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             # Création de l'utilisateur
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password1'])
#             user.save()

#             # Création du profil associé
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()

#             login(request, user)
#             messages.success(request, _("Inscription réussie. Bienvenue sur SOGENTIS !"))
#             return redirect('dashboard:index')
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