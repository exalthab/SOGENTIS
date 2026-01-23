from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .base import BaseRegistrationV2Form


class EconomicClientRegistrationV2Form(BaseRegistrationV2Form):
    address = forms.CharField(label=_("Adresse"), required=False, max_length=255)
    city = forms.CharField(label=_("Ville"), required=False, max_length=80)

    id_doc_type = forms.ChoiceField(
        label=_("Type de pièce"),
        choices=[("CNI", _("CNI")), ("PASSPORT", _("Passeport"))],
        required=False,
    )
    id_number = forms.CharField(label=_("Numéro de pièce"), max_length=64, required=False)
    id_front = forms.FileField(label=_("Pièce recto (optionnel)"), required=False)


class EconomicVendorRegistrationV2Form(BaseRegistrationV2Form):
    shop_name = forms.CharField(label=_("Nom de la boutique"), max_length=120, required=True)
    shop_address = forms.CharField(label=_("Adresse boutique"), max_length=255, required=True)

    # KYC vendeur
    id_doc_type = forms.ChoiceField(label=_("Type de pièce"), choices=[("CNI", _("CNI")), ("PASSPORT", _("Passeport"))], required=True)
    id_number = forms.CharField(label=_("Numéro de pièce"), max_length=64, required=True)
    id_front = forms.FileField(label=_("Pièce recto"), required=True)

    business_license = forms.FileField(label=_("Autorisation / Registre commerce"), required=True)
    tax_certificate = forms.FileField(label=_("Attestation fiscale (optionnel)"), required=False)
    bank_rib = forms.FileField(label=_("RIB (optionnel)"), required=False)


class EconomicB2BRegistrationV2Form(BaseRegistrationV2Form):
    company_name = forms.CharField(label=_("Nom de l’entreprise"), max_length=160, required=True)
    company_address = forms.CharField(label=_("Adresse entreprise"), max_length=255, required=True)
    legal_form = forms.CharField(label=_("Forme juridique"), max_length=60, required=False)

    rccm_number = forms.CharField(label=_("RCCM"), max_length=80, required=False)
    ninea_number = forms.CharField(label=_("NINEA / Identifiant"), max_length=80, required=False)

    # Docs entreprise
    rccm_file = forms.FileField(label=_("Document RCCM (optionnel)"), required=False)
    ninea_file = forms.FileField(label=_("Document NINEA (optionnel)"), required=False)
    statutes = forms.FileField(label=_("Statuts (optionnel)"), required=False)

    # Identity owner/representant
    id_doc_type = forms.ChoiceField(label=_("Type de pièce"), choices=[("CNI", _("CNI")), ("PASSPORT", _("Passeport"))], required=True)
    id_number = forms.CharField(label=_("Numéro de pièce"), max_length=64, required=True)
    id_front = forms.FileField(label=_("Pièce recto"), required=True)
