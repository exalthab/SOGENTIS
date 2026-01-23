# accounts_users/web/urls/registration_urls.py
from django.urls import path
from django.views.generic import TemplateView

from accounts_users.web.views.registration_choice import registration_choice_view
from accounts_users.web.views.social.social_registration_view import social_register_view
from accounts_users.web.views.economic.registration_economic import register_economic_view
from accounts_users.web.views.activation_web_views import activate_account_view, resend_activation_view

app_name = "registration"

urlpatterns = [
    # HUB (canonique)
    path("", registration_choice_view, name="choice"),
    # alias ancien (pour tes templates existants)
    path("choice/", registration_choice_view, name="registration_choice"),

    # Formulaires
    path("social/", social_register_view, name="social_register"),
    path("economic/", register_economic_view, name="register_economic"),

    # ✅ alias propre (recommandé) si on l’utilises ailleurs
    path("economic/choice/", register_economic_view, name="register_economic_choice"),

    path(
        "confirmation/",
        TemplateView.as_view(template_name="accounts_users/registration/register_done.html"),
        name="register_done",
    ),
    path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
    path("resend-activation/", resend_activation_view, name="resend_activation"),
]





# # accounts_users/web/urls/registration_urls.py
# from django.urls import path
# from django.views.generic import TemplateView
# from accounts_users.web.views.registration_choice import registration_choice_view
# from accounts_users.web.views.social.social_registration_view import social_register_view
# from accounts_users.web.views.economic.registration_economic import register_economic_view

# # from accounts_users.web.views.economic.registration_economic import register_economic_choice_view

# from accounts_users.web.views.activation_web_views import activate_account_view, resend_activation_view

# app_name = "registration"

# urlpatterns = [
#     path("", registration_choice_view, name="choice"),
#     path("social/", social_register_view, name="social_register"),
#     path("economic/", register_economic_view, name="register_economic"),
#     path(
#         "register/economic/choice/",
#     register_economic_view,
#         name="register_economic_choice",
#     ), 
#     # path(
#     #     "register/economic/choice/",
#     # register_economic_choice_view,
#     #     name="register_economic_choice",
#     # ),    

#     # path("registration/economic/", register_economic_view, name="register_economic"),

#     # path("register/", registration_choice_view, name="register_choice"),

#     # path("register/social/", social_register_view, name="social_register"),
#     # path("register/economic/", register_economic_view, name="register_economic"),
#     path(
#         "confirmation/",
#         TemplateView.as_view(template_name="accounts_users/registration/register_done.html"),
#         name="register_done",
#     ),
#     path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
#     path("resend-activation/", resend_activation_view, name="resend_activation"),
# ]
