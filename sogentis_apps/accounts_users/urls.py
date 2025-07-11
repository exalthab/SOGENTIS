#accounts_users/urls.py
from django.urls import path
# from accounts_users.views.registration import web_signup_view
from accounts_users.views.activation import activate_account_view
from django.contrib.auth.views import LoginView, LogoutView
from accounts_users.views.profiles import edit_profile_view
from django.contrib.auth import views as auth_views



app_name = "accounts_users"

urlpatterns = [
    # path('signup/', web_signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', activate_account_view, name='activate'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profiles/edit/', edit_profile_view, name='profile_edit'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    # path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    
]





# #accounts_users/urls.py -> 01/07
# from django.urls import path, include
# from accounts_users.web.views.registration_views import signup_view
# from accounts_users.web.views.profile_views import list_pending_profiles
# from django.contrib.auth import views as auth_views

# app_name = "accounts_users"

# urlpatterns = [
#     path("signup/", signup_view, name="signup"),
#     path('password_change/', auth_views.PasswordChangeView.as_view(
#         template_name='accounts_users/password_change.html'
#     ), name='password_change'),

#     path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
#         template_name='accounts_users/password_change_done.html'
#     ), name='password_change_done'),
    
    
#     # Authentification Django (connexion, changement mot de passe, etc.)
#     path('accounts/', include('django.contrib.auth.urls')),
    
#     path('', include('accounts_users.web.urls')),
#     path('admin/pending-profiles/', list_pending_profiles, name='list_pending_profiles')

# ]






# from django.urls import path, include

# app_name = "accounts_users"

# urlpatterns = [
#     path('', include('accounts_users.web.urls')),
# ]
