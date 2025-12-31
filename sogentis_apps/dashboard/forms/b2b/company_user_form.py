from django import forms
from economic.b2b.models import CompanyUser


class CompanyUserForm(forms.ModelForm):
    class Meta:
        model = CompanyUser
        fields = [
            "user",
            "role",
            "is_active",
        ]
