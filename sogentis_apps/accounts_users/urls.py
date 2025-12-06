# #accounts_users/urls.py
from django.urls import path
# from accounts_users.views.activation import activate_account_view
from accounts_users.views.profiles import edit_profile_view

app_name = "accounts_users"

urlpatterns = [
    # path('activate/<uidb64>/<token>/', activate_account_view, name='activate'),
    path('profiles/edit/', edit_profile_view, name='profile_edit'),
    # ... autre logique spécifique, mais PAS de login/reset ici !
]
