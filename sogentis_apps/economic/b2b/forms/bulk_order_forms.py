# economic/b2b/forms/bulk_order_forms.py
from django import forms

from economic.b2b.models import BulkOrder, BulkOrderItem


class BulkOrderForm(forms.ModelForm):
    class Meta:
        model = BulkOrder
        fields = ["reference", "notes"]
        widgets = {
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class BulkOrderItemForm(forms.ModelForm):
    class Meta:
        model = BulkOrderItem
        fields = ["product", "quantity", "unit_price"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }



# # economic/b2b/forms/bulk_order_forms.py
# from django import forms
# from django.forms import inlineformset_factory
# from django.utils.translation import gettext_lazy as _

# from ..models import BulkOrder, BulkOrderItem


# class BulkOrderForm(forms.ModelForm):
#     class Meta:
#         model = BulkOrder
#         fields = ("reference", "notes")
#         widgets = {
#             "reference": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Référence interne (optionnel)")}),
#             "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
#         }


# class BulkOrderItemForm(forms.ModelForm):
#     class Meta:
#         model = BulkOrderItem
#         fields = ("product", "quantity", "unit_price")
#         widgets = {
#             "product": forms.Select(attrs={"class": "form-select"}),
#             "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
#             "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
#         }


# BulkOrderItemFormSet = inlineformset_factory(
#     BulkOrder,
#     BulkOrderItem,
#     form=BulkOrderItemForm,
#     extra=1,
#     can_delete=True,
# )
