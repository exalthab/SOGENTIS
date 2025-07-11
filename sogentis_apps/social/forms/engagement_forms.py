# #social/forms/engagement_forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from social.models import Engagement

class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        fields = ['title', 'description', 'date']
        labels = {
            'title': _("Titre de l'engagement"),
            'description': _("Description"),
            'date': _("Date de l’engagement"),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Titre de l'engagement")
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _("Décrivez votre engagement")
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
