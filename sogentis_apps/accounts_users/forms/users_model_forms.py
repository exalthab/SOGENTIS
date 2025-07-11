# accounts_users/forms/users_model_forms.py
from django import forms
from accounts_users.models.users import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserModelForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "is_active", "is_staff"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }




## accounts_users/forms/users_model_forms.py ->01/07
# from django import forms
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class UserModelForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['email', 'is_active', 'is_staff']
#         widgets = {
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(),
#             'is_staff': forms.CheckboxInput(),
#         }
