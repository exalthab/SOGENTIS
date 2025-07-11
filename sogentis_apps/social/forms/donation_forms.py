# social/forms/donation_forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from social.models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            'donor_name', 'email', 'amount', 'project', 'message', 'monthly'
        ]
        labels = {
            'donor_name': _("Nom du donateur"),
            'email': _("Adresse email"),
            'amount': _("Montant du don (FCFA)"),
            'project': _("Projet à soutenir"),
            'message': _("Message (optionnel)"),
            'monthly': _("Faire ce don chaque mois"),
        }
        widgets = {
            'donor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Votre nom complet")}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _("Votre adresse email")}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _("Montant en FCFA")}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _("Votre message (optionnel)")}),
            'monthly': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_monthly'}),
        }











# # # social/forms/donation_forms.py
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from social.models import Donation

# class DonationForm(forms.ModelForm):
#     class Meta:
#         model = Donation
#         fields = ['donor_name', 'email', 'amount', 'project', 'message']
#         labels = {
#             'donor_name': _("Nom du donateur"),
#             'email': _("Adresse email"),
#             'amount': _("Montant du don (FCFA)"),
#             'project': _("Projet à soutenir"),
#             'message': _("Message (optionnel)"),
#         }
#         widgets = {
#             'donor_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': _("Votre nom complet")
#             }),
#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': _("Votre adresse email")
#             }),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': _("Montant en FCFA")
#             }),
#             'project': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'message': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': _("Votre message (optionnel)")
#             }),
#         }
