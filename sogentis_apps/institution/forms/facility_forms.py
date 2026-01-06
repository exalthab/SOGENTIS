from django import forms

from institution.models.facility import Facility


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = (
            "name",
            "facility_type",
            "short_description",
            "description",
            "address",
            "city",
            "country",
            "phone",
            "email",
            "is_active",
        )
