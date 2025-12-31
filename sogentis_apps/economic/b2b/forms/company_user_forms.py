from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from economic.b2b.models import CompanyUser

User = get_user_model()


class CompanyUserCreateForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    role = forms.ChoiceField(choices=CompanyUser.ROLE_CHOICES)


class CompanyUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CompanyUser
        fields = ("role", "is_active")
