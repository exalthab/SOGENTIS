# accounts_users/forms/resend_activation_form.py
from django import forms
from django.utils.translation import gettext_lazy as _

class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
    )



## accounts_users/forms/resend_activation_form.py ->01/07
# from django import forms
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class ResendActivationForm(forms.Form):
#     email = forms.EmailField(label="Adresse e-mail")

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         try:
#             user = User.objects.get(email=email)
#             if user.is_active:
#                 raise forms.ValidationError("Ce compte est déjà activé.")
#         except User.DoesNotExist:
#             raise forms.ValidationError("Aucun compte associé à cette adresse.")
#         return email
