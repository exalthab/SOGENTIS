from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .base import BaseRegistrationV2Form
from accounts_users.models.membership_role import MembershipRole  # selon tes anciens rôles


class SocialRegistrationV2Form(BaseRegistrationV2Form):
    # Champs “anciens social”
    role = forms.ModelChoiceField(
        queryset=MembershipRole.objects.all().order_by("code"),
        label=_("Type d’adhésion"),
        required=True,
        empty_label=_("Choisir un rôle"),
    )
    message = forms.CharField(
        label=_("Message"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    # Identification / pièces jointes (KYC social)
    id_doc_type = forms.ChoiceField(
        label=_("Type de pièce"),
        choices=[("CNI", _("CNI")), ("PASSPORT", _("Passeport")), ("PERMIS", _("Permis"))],
        required=True,
    )
    id_number = forms.CharField(label=_("Numéro de pièce"), max_length=64, required=True)

    id_front = forms.FileField(label=_("Pièce recto"), required=True)
    id_back = forms.FileField(label=_("Pièce verso"), required=False)
    selfie = forms.FileField(label=_("Selfie (optionnel)"), required=False)

    proof_address = forms.FileField(label=_("Justificatif de domicile (optionnel)"), required=False)
