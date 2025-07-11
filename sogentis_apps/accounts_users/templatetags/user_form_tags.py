from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={
        **field.field.widget.attrs,  # conserve les attributs déjà existants
        'class': f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()
    })
