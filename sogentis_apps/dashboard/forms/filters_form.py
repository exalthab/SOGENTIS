# #dashboard/forms/filters_form.py
from django import forms
from django.utils.translation import gettext_lazy as _

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(
        label=_("Date de début"),
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
            "placeholder": _("Date de début")
        })
    )
    end_date = forms.DateField(
        label=_("Date de fin"),
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
            "placeholder": _("Date de fin")
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError(_("La date de début doit précéder la date de fin."))
        return cleaned_data

class ProjectStatusFilterForm(forms.Form):
    status = forms.ChoiceField(
        label=_("Statut du projet"),
        choices=[
            ("", _("Tous")),
            ("active", _("Actif")),
            ("completed", _("Terminé")),
        ],
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )



# from django import forms
# from django.utils.translation import gettext_lazy as _


# class DateRangeFilterForm(forms.Form):
#     start_date = forms.DateField(
#         label=_("Date de début"),
#         required=False,
#         widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
#     )
#     end_date = forms.DateField(
#         label=_("Date de fin"),
#         required=False,
#         widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
#     )


# class ProjectStatusFilterForm(forms.Form):
#     status = forms.ChoiceField(
#         label=_("Statut du projet"),
#         choices=[
#             ("", _("Tous")),
#             ("active", _("Actif")),
#             ("completed", _("Terminé")),
#         ],
#         required=False,
#         widget=forms.Select(attrs={"class": "form-select"})
#     )
