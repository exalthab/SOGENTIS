from django import forms
from django.utils.translation import gettext_lazy as _

class DownloadCodeForm(forms.Form):
    code = forms.CharField(
        label=_("Code de téléchargement"),
        max_length=64,
        widget=forms.TextInput(attrs={
            "placeholder": _("Collez votre code ici"),
            "class": "form-control"
        })
    )
