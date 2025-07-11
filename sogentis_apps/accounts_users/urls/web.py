from django.urls import path
from accounts_users.views.activation import activate_account_view

urlpatterns = [
    path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
]
