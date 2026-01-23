# accounts_users/urls.py
from django.urls import path, include

app_name = "accounts_users"

urlpatterns = [
    path(
        "web/",
        include(
            ("accounts_users.web.urls", "web"),
            namespace="web",
        ),
    ),
]






# # accounts_users/urls.py

# from django.urls import path

# # On importe la vue *web* correcte
# from accounts_users.web.views.profile_web_views import profile_edit_view

# app_name = "accounts_users"

# urlpatterns = [
#     # Modification du profil utilisateur
#     path("profile/edit/", profile_edit_view, name="profile_edit"),
# ]





# # #accounts_users/urls.py
# from django.urls import path
# # from accounts_users.views.activation import activate_account_view
# from accounts_users.views.profiles import edit_profile_view

# app_name = "accounts_users"

# urlpatterns = [
#     # path('activate/<uidb64>/<token>/', activate_account_view, name='activate'),
#     path('profiles/edit/', edit_profile_view, name='profile_edit'),
#     # ... autre logique spécifique, mais PAS de login/reset ici !
# ]
