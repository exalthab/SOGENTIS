from django import forms
from economic.ecommerce.models import Product


class VendorProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "sku",
            "price",
            "stock",
            "is_active",
            # "name",
            # "short_description",
            # "description",
        ]
