from __future__ import annotations
import json
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def cookie_allowed(context, category: str) -> bool:
    """
    Usage:
      {% cookie_allowed "analytics" as ok_analytics %}
      {% if ok_analytics %}...{% endif %}
    """
    request = context.get("request")
    if not request:
        return False

    raw = request.COOKIES.get("cookie_consent")
    if not raw:
        return False

    try:
        data = json.loads(raw)
    except Exception:
        return False

    if category == "necessary":
        return True
    return bool(data.get(category))
