# accounts_users/forms/user_forms.py

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserEmailUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)
