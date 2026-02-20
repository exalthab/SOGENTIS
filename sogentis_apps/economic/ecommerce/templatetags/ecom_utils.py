# economic/ecommerce/templatetags/ecom_utils.py
from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def has_attr(obj, name: str) -> bool:
    try:
        return hasattr(obj, str(name))
    except Exception:
        return False
