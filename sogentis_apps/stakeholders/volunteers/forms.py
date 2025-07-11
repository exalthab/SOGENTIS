from django import forms
from .models import Volunteer

class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['first_name', 'last_name', 'email', 'phone', 'motivation']
