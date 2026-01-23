# # accounts_users/web/registration_urls.py
# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views

# from accounts_users.web.views import (
#     auth_login_web_views,
#     profile_web_views,
# )
# from accounts_users.web.views import profile
# from accounts_users.web.views.auth_login_choice import auth_choice_view
# from accounts_users.web.views.auth_login_web_views import login_view
# from accounts_users.web.views.activation_web_views import (
#     activate_account_view,
#     resend_activation_view,
# )
# from accounts_users.web.views.social.social_registration_view import social_register_view
# from accounts_users.web.views.economic.registration_economic import (
#     register_economic_view,
#     register_economic_choice_view,
# )
# from accounts_users.web.views.registration_choice import registration_choice_view

# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )
# from accounts_users.web.views.validation import check_email_availability
# from accounts_users.web.views.email_otp_views import (
#     send_email_otp,
#     verify_email_otp,
# )

# app_name = "web"

# urlpatterns = [
#     # ============================================================
#     # AUTHENTIFICATION
#     # ============================================================
#     path("auth/", auth_choice_view, name="auth_choice"),
#     path("login/", auth_login_web_views.login_view, name="login"),
#     path("login/social/", login_view, name="social_login"),
#     path("login/economic/", login_view, name="login_economic"),
#     path("logout/", auth_login_web_views.logout_view, name="logout"),

#     # ============================================================
#     # INSCRIPTION — ACTIVATION (modulaire)
#     # ============================================================
#     path("", registration_choice_view, name="choice"),

#     path("register/social/", social_register_view, name="social_register"),
#     path("registration/economic/", register_economic_view, name="register_economic"),

#     path(
#         "register/confirmation/",
#         TemplateView.as_view(template_name="accounts_users/registration/register_done.html"),
#         name="register_done",
#     ),
#     path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
#     path("resend-activation/", resend_activation_view, name="resend_activation"),

#     # ============================================================
#     # PROFIL UTILISATEUR
#     # ============================================================
#     path("profile/", profile.myprofile_view, name="profile"),
#     path("profile/edit/", profile_web_views.profile_edit_view, name="profile_edit"),
#     path("profile/pending/", profile_web_views.profile_pending_notice, name="profile_pending_notice"),

#     # ============================================================
#     # PASSWORD CHANGE (connecté)
#     # ============================================================
#     path(
#         "password-change/",
#         auth_views.PasswordChangeView.as_view(
#             template_name="accounts_users/registration/password_change_form.html"
#         ),
#         name="password_change",
#     ),
#     path(
#         "password-change/done/",
#         auth_views.PasswordChangeDoneView.as_view(
#             template_name="accounts_users/registration/password_change_done.html"
#         ),
#         name="password_change_done",
#     ),

#     # ============================================================
#     # PASSWORD RESET (oubli)
#     # ============================================================
#     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
#     path("password_reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
#     path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
#     path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),

#     # ============================================================
#     # AJAX
#     # ============================================================
#     path("ajax/check-email/", check_email_availability, name="check_email"),
#     path("ajax/email/send-otp/", send_email_otp, name="send_email_otp"),
#     path("ajax/email/verify-otp/", verify_email_otp, name="verify_email_otp"),
# ]










# # accounts_users/web/urls.py
# from django.urls import path, include
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views

# from accounts_users.web.views import (
#     auth_login_web_views,
#     profile_web_views,
# )
# from accounts_users.web.views import profile
# from accounts_users.web.views.auth_login_choice import auth_choice_view
# from accounts_users.web.views.auth_login_web_views import login_view
# from accounts_users.web.views.activation_web_views import (
#     activate_account_view,
#     resend_activation_view,
# )
# from accounts_users.web.views.social.social_registration_view import social_register_view
# from accounts_users.web.views.economic.registration_economic import (
#     register_economic_view,
#     register_economic_choice_view,
# )
# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )
# from accounts_users.web.views.validation import check_email_availability
# from accounts_users.web.views.email_otp_views import (
#     send_email_otp,
#     verify_email_otp,
# )

# app_name = "web"

# urlpatterns = [
#     # ============================================================
#     # AUTHENTIFICATION
#     # ============================================================
#     path("auth/", auth_choice_view, name="auth_choice"),
#     path("login/", auth_login_web_views.login_view, name="login"),
#     path("login/social/", login_view, name="social_login"),
#     path("login/economic/", login_view, name="login_economic"),
#     path("logout/", auth_login_web_views.logout_view, name="logout"),

#     # ============================================================
#     # INSCRIPTION — ACTIVATION (modulaire)
#     # ============================================================
#     path(
#         "registration/",
#         include(("accounts_users.web.urls.registration_urls", "registration"),
#                 namespace="registration"),
#     ),
#     # path(
#     #     "register/economic/choice/",
#     #     register_economic_choice_view,
#     #     name="register_economic_choice",
#     # ),
#     # path("register/", registration_choice_view, name="register_choice"),

#     path("register/social/", social_register_view, name="social_register"),
#     path("register/economic/", register_economic_view, name="register_economic"),

#     path(
#         "register/confirmation/",
#         TemplateView.as_view(
#             template_name="accounts_users/registration/register_done.html"
#         ),
#         name="register_done",
#     ),
#     path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
#     path("resend-activation/", resend_activation_view, name="resend_activation"),

#     # ============================================================
#     # PROFIL UTILISATEUR
#     # ============================================================
#     path("profile/", profile.myprofile_view, name="profile"),
#     path("profile/edit/", profile_web_views.profile_edit_view, name="profile_edit"),
#     path(
#         "profile/pending/",
#         profile_web_views.profile_pending_notice,
#         name="profile_pending_notice",
#     ),

#     # ============================================================
#     # PASSWORD CHANGE (connecté)
#     # ============================================================
#     path(
#         "password-change/",
#         auth_views.PasswordChangeView.as_view(
#             template_name="accounts_users/registration/password_change_form.html"
#         ),
#         name="password_change",
#     ),
#     path(
#         "password-change/done/",
#         auth_views.PasswordChangeDoneView.as_view(
#             template_name="accounts_users/registration/password_change_done.html"
#         ),
#         name="password_change_done",
#     ),

#     # ============================================================
#     # PASSWORD RESET (oubli)
#     # ============================================================
#     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
#     path(
#         "password_reset/done/",
#         CustomPasswordResetDoneView.as_view(),
#         name="password_reset_done",
#     ),
#     path(
#         "reset/<uidb64>/<token>/",
#         CustomPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm",
#     ),
#     path(
#         "reset/done/",
#         CustomPasswordResetCompleteView.as_view(),
#         name="password_reset_complete",
#     ),

#     # ============================================================
#     # AJAX
#     # ============================================================
#     path("ajax/check-email/", check_email_availability, name="check_email"),
#     path("ajax/email/send-otp/", send_email_otp, name="send_email_otp"),
#     path("ajax/email/verify-otp/", verify_email_otp, name="verify_email_otp"),
# ]





# # accounts_users/web/urls.py
# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views

# from accounts_users.web.views import (
#     auth_login_web_views,
#     profile_web_views,
# )
# from accounts_users.web.views import profile
# from accounts_users.web.views.auth_login_choice import auth_choice_view
# from accounts_users.web.views.auth_login_web_views import login_view
# from accounts_users.web.views.activation_web_views import (
#     activate_account_view,
#     resend_activation_view,
# )
# from accounts_users.web.views.registration_choice import registration_choice_view
# from accounts_users.web.views.social.social_registration_view import social_register_view
# from accounts_users.web.views.economic.registration_economic import (
#     register_economic_view,
#     register_economic_choice_view,
# )
# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )
# from accounts_users.web.views.validation import check_email_availability
# from accounts_users.web.views.email_otp_views import (
#     send_email_otp,
#     verify_email_otp,
# )

# app_name = "web"

# urlpatterns = [
#     # ============================================================
#     # AUTHENTIFICATION
#     # ============================================================
#     path("auth/", auth_choice_view, name="auth_choice"),
#     path("login/", auth_login_web_views.login_view, name="login"),
#     path("login/social/", login_view, name="social_login"),
#     path("login/economic/", login_view, name="login_economic"),
#     path("logout/", auth_login_web_views.logout_view, name="logout"),

#     # ============================================================
#     # INSCRIPTION — ACTIVATION
#     # ============================================================
#     path("register/", registration_choice_view, name="register_choice"),
#     path("register/social/", social_register_view, name="social_register"),
#     path("register/economic/", register_economic_view, name="register_economic"),
#     path(
#         "register/economic/choice/",
#         register_economic_choice_view,
#         name="register_economic_choice",
#     ),
#     path(
#         "register/confirmation/",
#         TemplateView.as_view(
#             template_name="accounts_users/registration/register_done.html"
#         ),
#         name="register_done",
#     ),
#     path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
#     path("resend-activation/", resend_activation_view, name="resend_activation"),

#     # ============================================================
#     # PROFIL UTILISATEUR
#     # ============================================================
#     path("profile/", profile.myprofile_view, name="profile"),
#     path("profile/edit/", profile_web_views.profile_edit_view, name="profile_edit"),
#     path(
#         "profile/pending/",
#         profile_web_views.profile_pending_notice,
#         name="profile_pending_notice",
#     ),

#     # ============================================================
#     # PASSWORD CHANGE (connecté)
#     # ============================================================
#     path(
#         "password-change/",
#         auth_views.PasswordChangeView.as_view(
#             template_name="accounts_users/registration/password_change_form.html"
#         ),
#         name="password_change",
#     ),
#     path(
#         "password-change/done/",
#         auth_views.PasswordChangeDoneView.as_view(
#             template_name="accounts_users/registration/password_change_done.html"
#         ),
#         name="password_change_done",
#     ),

#     # ============================================================
#     # PASSWORD RESET (oubli)
#     # ============================================================
#     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
#     path(
#         "password_reset/done/",
#         CustomPasswordResetDoneView.as_view(),
#         name="password_reset_done",
#     ),
#     path(
#         "reset/<uidb64>/<token>/",
#         CustomPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm",
#     ),
#     path(
#         "reset/done/",
#         CustomPasswordResetCompleteView.as_view(),
#         name="password_reset_complete",
#     ),

#     # ============================================================
#     # AJAX
#     # ============================================================
#     path("ajax/check-email/", check_email_availability, name="check_email"),
#     path("ajax/email/send-otp/", send_email_otp, name="send_email_otp"),
#     path("ajax/email/verify-otp/", verify_email_otp, name="verify_email_otp"),
# ]









# # accounts_users/web/urls.py

# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views

# # Import groupé des vues
# from accounts_users.web.views import (
#     auth_login_web_views,
#     profile_web_views,
# )
# from accounts_users.web.views import profile

# from accounts_users.web.views.auth_login_choice import auth_choice_view
# from accounts_users.web.views.auth_login_web_views import login_view

# # Activation & renvoi lien activation
# from accounts_users.web.views.activation_web_views import (
#     activate_account_view,
#     resend_activation_view,
# )

# # from accounts_users.web.views.social import registration_views
# from accounts_users.web.views.registration_choice import registration_choice_view
# from accounts_users.web.views.social.social_registration_view import social_register_view
# from accounts_users.web.views.economic.registration_economic import register_economic_view, register_economic_choice_view

# # Password reset personnalisé
# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )

# from accounts_users.web.views.validation import check_email_availability
# # from accounts_users.web.views.phone_otp_views import (
# #     send_phone_otp,
# #     verify_phone_otp,
# # )
# from accounts_users.web.views.email_otp_views import (
#     send_email_otp,
#     verify_email_otp,
# )
# app_name = "accounts_users"

# urlpatterns = [

#     # ============================================================
#     # AUTHENTIFICATION
#     # ============================================================
#     path("auth/", auth_choice_view, name="auth_choice"),

#     path("login/", auth_login_web_views.login_view, name="login"),
    
#     # Entrées contextuelles
#     path("login/social/", login_view, name="social_login"),
#     # path("login/social/", login_view, name="login_social"),
#     path("login/economic/", login_view, name="login_economic"),

#     path("logout/", auth_login_web_views.logout_view, name="logout"),

#     # ============================================================
#     # INSCRIPTION — ACTIVATION DE COMPTE
#     # ============================================================
#     path("register/", registration_choice_view, name="register_choice"),
#     path("register/social/", social_register_view, name="social_register"),
#     path(
#         "register/economic/",
#         register_economic_view,
#         name="register_economic",
#     ),
#     path(
#         "register/economic/choice/",
#         register_economic_choice_view,
#         name="register_economic_choice",
#     ),
    
#     # path("register/", registration_views.register_view, name="register"),
#     path(
#         "register/confirmation/",
#         TemplateView.as_view(
#             template_name="accounts_users/registration/register_done.html"
#         ),
#         name="register_done"
#     ),
#     path(
#         "activate/<uidb64>/<token>/",
#         activate_account_view,
#         name="activate"
#     ),
#     path(
#         "resend-activation/",
#         resend_activation_view,
#         name="resend_activation"
#     ),

#     # ============================================================
#     # PROFIL UTILISATEUR
#     # ============================================================
#     path("profile/",  
#         profile.myprofile_view,
#         name="profile"),
    
#     path(
#         "profile/edit/",
#         profile_web_views.profile_edit_view,
#         name="profile_edit"
#     ),
#     path(
#         "profile/pending/",
#         profile_web_views.profile_pending_notice,
#         name="profile_pending_notice"
#     ),

#     # ============================================================
#     # PASSWORD CHANGE (connecté)
#     # ============================================================
#     path(
#         "password-change/",
#         auth_views.PasswordChangeView.as_view(
#             template_name="accounts_users/registration/password_change_form.html"
#         ),
#         name="password_change",
#     ),
#     path(
#         "password-change/done/",
#         auth_views.PasswordChangeDoneView.as_view(
#             template_name="accounts_users/registration/password_change_done.html"
#         ),
#         name="password_change_done",
#     ),

#     # ============================================================
#     # PASSWORD RESET (oubli de mot de passe)
#     # ============================================================
#     path(
#         "password_reset/",
#         CustomPasswordResetView.as_view(),
#         name="password_reset"
#     ),
#     path(
#         "password_reset/done/",
#         CustomPasswordResetDoneView.as_view(),
#         name="password_reset_done"
#     ),
#     path(
#         "reset/<uidb64>/<token>/",
#         CustomPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm"
#     ),
#     path(
#         "reset/done/",
#         CustomPasswordResetCompleteView.as_view(),
#         name="password_reset_complete"
#     ),
    
#     path("ajax/check-email/", check_email_availability, name="check_email"),
#     path("ajax/email/send-otp/", send_email_otp, name="send_email_otp"),
#     path("ajax/email/verify-otp/", verify_email_otp, name="verify_email_otp"),
#     # path("ajax/phone/send-otp/", send_phone_otp, name="send_phone_otp"),
#     # path("ajax/phone/verify-otp/", verify_phone_otp, name="verify_phone_otp"),

# ]








# # accounts_users/web/urls.py

# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views

# # Import groupé des modules
# from accounts_users.web.views import (
#     auth_web_views,
#     profile_web_views,
#     registration_views,
#     profile_view,
# )

# # Activation & renvoi lien activation
# from accounts_users.web.views.registration_views import (
#     activate_view,
#     resend_activation_view,
# )

# # Password reset
# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )

# app_name = "accounts_users_web"

# urlpatterns = [

#     # ============================================================
#     # AUTHENTIFICATION
#     # ============================================================
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),

#     # ============================================================
#     # INSCRIPTION — ACTIVATION DE COMPTE
#     # ============================================================
#     path("signup/", registration_views.signup_view, name="signup"),

#     path(
#         "signup/confirmation/",
#         TemplateView.as_view(
#             template_name="accounts_users/registration/signup_done.html"
#         ),
#         name="signup_done"
#     ),

#     # Activation de compte
#     path(
#         "activate/<uidb64>/<token>/",
#         activate_view,
#         name="activate"
#     ),

#     # Renvoi du lien d’activation
#     path(
#         "resend-activation/",
#         resend_activation_view,
#         name="resend_activation"
#     ),

#     # ============================================================
#     # PROFIL UTILISATEUR
#     # ============================================================
#     path("profile/", profile_view, name="profile"),

#     # Modifier son propre profil
#     path(
#         "profile/edit/",
#         profile_web_views.profile_edit_view,
#         name="profile_edit"
#     ),

#     # Profil en attente
#     path(
#         "profile/pending/",
#         profile_web_views.profile_pending_notice,
#         name="profile_pending_notice"
#     ),

#     # ============================================================
#     # PASSWORD CHANGE (connecté)
#     # ============================================================
#     path(
#         "password-change/",
#         auth_views.PasswordChangeView.as_view(
#             template_name="accounts_users/registration/password_change_form.html"
#         ),
#         name="password_change",
#     ),

#     path(
#         "password-change/done/",
#         auth_views.PasswordChangeDoneView.as_view(
#             template_name="accounts_users/registration/password_change_done.html"
#         ),
#         name="password_change_done",
#     ),

#     # ============================================================
#     # PASSWORD RESET (oubli de mot de passe)
#     # ============================================================
#     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),

#     path(
#         "password_reset/done/",
#         CustomPasswordResetDoneView.as_view(),
#         name="password_reset_done"
#     ),

#     path(
#         "reset/<uidb64>/<token>/",
#         CustomPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm"
#     ),

#     path(
#         "reset/done/",
#         CustomPasswordResetCompleteView.as_view(),
#         name="password_reset_complete"
#     ),
# ]






# # accounts_users/web/urls.py

# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views

# from accounts_users.web.views import (
#     auth_web_views,
#     profile_web_views,
#     registration_views,
# )

# from accounts_users.web.views.registration_views import (
#     activate_view,
#     resend_activation_view,
# )

# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )

# app_name = "accounts_users_web"

# urlpatterns = [

#     # -------------------------------------------
#     # AUTHENTIFICATION
#     # -------------------------------------------
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),

#     # -------------------------------------------
#     # INSCRIPTION & ACTIVATION
#     # -------------------------------------------
#     path("signup/", registration_views.signup_view, name="signup"),
#     path(
#         "signup/confirmation/",
#         TemplateView.as_view(template_name="accounts_users/registration/signup_done.html"),
#         name="signup_done"
#     ),

#     # ⚠️ UTILISER /activate/ POUR COHÉRENCE AVEC LES EMAILS
#     path("activate/<uidb64>/<token>/", activate_view, name="activate"),

#     path("resend-activation/", resend_activation_view, name="resend_activation"),

#     # -------------------------------------------
#     # PROFIL UTILISATEUR
#     # -------------------------------------------

#     # Modifier le profil (manquant dans ton code)
#     path("profile/edit/", profile_web_views.profile_edit_view, name="profile_edit"),

#     # Page "profil en attente"
#     path("profile/pending/", profile_web_views.profile_pending_notice, name="profile_pending_notice"),

#     # -------------------------------------------
#     # PASSWORD CHANGE (utilisateur connecté)
#     # -------------------------------------------
#     path(
#         "password-change/",
#         auth_views.PasswordChangeView.as_view(
#             template_name="accounts_users/registration/password_change_form.html"
#         ),
#         name="password_change",
#     ),

#     path(
#         "password-change/done/",
#         auth_views.PasswordChangeDoneView.as_view(
#             template_name="accounts_users/registration/password_change_done.html"
#         ),
#         name="password_change_done",
#     ),

#     # -------------------------------------------
#     # PASSWORD RESET (oubli de mot de passe)
#     # -------------------------------------------
#     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
#     path("password_reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),

#     path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
#     path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
# ]









# # accounts_users/web/urls.py

# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views
# from accounts_users.web.views import (
#     auth_web_views, profile_web_views, registration_views
# )
# from accounts_users.web.views.registration_views import activate_view, resend_activation_view
# from accounts_users.web.views.password_views import (
#     CustomPasswordResetView,
#     CustomPasswordResetDoneView,
#     CustomPasswordResetConfirmView,
#     CustomPasswordResetCompleteView,
# )

# app_name = "accounts_users_web"

# urlpatterns = [
#     # Authentification
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),

#     # Inscription & activation
#     path("signup/", registration_views.signup_view, name="signup"),
#     path("signup/confirmation/", TemplateView.as_view(
#         template_name="accounts_users/registration/signup_done.html"
#     ), name="signup_done"),
#     path("activer/<uidb64>/<token>/", activate_view, name="activate"),
#     path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),

#     # Profil (état en attente)
#     path('profile/pending/', profile_web_views.profile_pending_notice, name='profile_pending_notice'),

#     # --- Password change (connecté) ---
#     path('password-change/', auth_views.PasswordChangeView.as_view(
#         template_name='accounts_users/registration/password_change_form.html'
#     ), name='password_change'),
#     path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
#         template_name='accounts_users/registration/password_change_done.html'
#     ), name='password_change_done'),

#     # --- Password reset (oubli, 100% CBV custom) ---
#     path(
#         'password_reset/',
#         CustomPasswordResetView.as_view(),
#         name='password_reset'
#     ),
#     path(
#         'password_reset/done/',
#         CustomPasswordResetDoneView.as_view(),
#         name='password_reset_done'
#     ),
#     path(
#         "reset/<uidb64>/<token>/",
#         CustomPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm"
#     ),
#     path(
#         "reset/done/",
#         CustomPasswordResetCompleteView.as_view(),
#         name="password_reset_complete"
#     ),

#     # Si besoin, active la vue custom function-based ci-dessous avec un nom UNIQUE, sans collision
#     # path("password-reset-custom/", password_views.password_reset_request, name="custom_password_reset"),
# ]









# from django.urls import path
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views
# from accounts_users.web.views import (
#     auth_web_views, password_views, registration_views, profile_views
# )
# from accounts_users.web.views.registration_views import activate_view, resend_activation_view

# app_name = "accounts_users_web"

# urlpatterns = [
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),
#     path("signup/", registration_views.signup_view, name="signup"),
#     path("signup/confirmation/", TemplateView.as_view(
#         template_name="accounts_users/registration/signup_done.html"
#     ), name="signup_done"),
#     path("activer/<uidb64>/<token>/", activate_view, name="activate"),
#     path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),
#     path('profile/pending/', profile_views.profile_pending_notice, name='profile_pending_notice'),

#     # FLOW DJANGO natif (conseillé) pour la réinitialisation
#     path("password_reset/", auth_views.PasswordResetView.as_view(
#             template_name="accounts_users/registration/password_reset_form.html"
#         ), name="password_reset"),
#     path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
#             template_name="accounts_users/registration/password_reset_done.html"
#         ), name="password_reset_done"),
#     path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
#             template_name="accounts_users/registration/password_reset_confirm.html"
#         ), name="password_reset_confirm"),
#     path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
#             template_name="accounts_users/registration/password_reset_complete.html"
#         ), name="password_reset_complete"),

#     # (optionnel) Si tu veux vraiment garder ta vue custom, renomme-la pour éviter tout conflit !
#     path("password-reset/", password_views.password_reset_request, name="custom_password_reset"),
# ]






#29/07/2025
# from django.urls import path
# from django.views.generic import TemplateView
# from accounts_users.web.views import (
#     auth_web_views, password_views, registration_views, profile_views
# )
# from accounts_users.web.views.registration_views import activate_view, resend_activation_view

# app_name = "accounts_users_web"

# urlpatterns = [
#     path("login/", auth_web_views.login_view, name="login"),
#     path("logout/", auth_web_views.logout_view, name="logout"),
#     path("signup/", registration_views.signup_view, name="signup"),
#     path("password-reset/", password_views.password_reset_request, name="password_reset"),

#     path("signup/confirmation/", TemplateView.as_view(
#         template_name="accounts_users/registration/signup_done.html"
#     ), name="signup_done"),

#     path("activer/<uidb64>/<token>/", activate_view, name="activate"),
#     path("renvoyer-lien-activation/", resend_activation_view, name="resend_activation"),

#     path('profile/pending/', profile_views.profile_pending_notice, name='profile_pending_notice'),
# ]
