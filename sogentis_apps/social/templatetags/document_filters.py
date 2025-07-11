from django import template
from social.models.document_access import DocumentPurchase

register = template.Library()

@register.filter
def has_purchase(doc, user):
    if not user.is_authenticated:
        return False
    return DocumentPurchase.objects.filter(user=user, publication=doc).exists()
