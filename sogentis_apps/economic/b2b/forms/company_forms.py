# economic/b2b/forms/company_forms.py
from django import forms
from economic.b2b.models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "email", "phone", "country", "city", "address", "website", "status", "is_active"]
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }





# # economic/b2b/forms/company_user_forms.py
# from django import forms
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models import CompanyUser


# class CompanyUserCreateForm(forms.Form):
#     email = forms.EmailField(label=_("Email"))
#     role = forms.ChoiceField(label=_("Rôle"), choices=CompanyUser.ROLE_CHOICES)


# class CompanyUserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = CompanyUser
#         fields = ("role", "is_active")







# # /economic/b2b/forms/company_user_forms.py
# from django import forms
# from django.contrib.auth import get_user_model
# from django.utils.translation import gettext_lazy as _

# from economic.b2b.models import CompanyUser

# User = get_user_model()


# class CompanyUserCreateForm(forms.Form):
#     email = forms.EmailField(label=_("Email"))
#     role = forms.ChoiceField(choices=CompanyUser.ROLE_CHOICES)


# class CompanyUserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = CompanyUser
#         fields = ("role", "is_active")
