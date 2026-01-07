# core/templatetags/domain_urls.py
from django import template
from django.conf import settings
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def domain_url(context, domain_key: str, viewname: str, *args, **kwargs) -> str:
    """
    Usage:
      {% domain_url 'COMMERCIAL' 'economic:index' %}
      {% domain_url 'COMMERCIAL' 'economic:ecommerce:index' %}
      {% domain_url 'APP' 'accounts_users:login' %}
    """
    base = getattr(settings, f"{domain_key}_BASE_URL", "") or ""
    if not base:
        return ""

    try:
        path = reverse(viewname, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return ""

    return base.rstrip("/") + path
