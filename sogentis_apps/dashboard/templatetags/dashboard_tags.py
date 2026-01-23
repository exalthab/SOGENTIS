# dashboard/templatetags/dashboard_tags.py
from __future__ import annotations

from typing import Any

from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


# -----------------------------
# Filters
# -----------------------------
@register.filter
def pluck(data: Any, key: str):
    """
    Extrait les valeurs associées à la clé 'key' depuis une liste de dict.
    {{ data|pluck:"key" }}
    """
    if not isinstance(data, (list, tuple)):
        return []
    out = []
    for item in data:
        if isinstance(item, dict):
            out.append(item.get(key))
        else:
            out.append(None)
    return out


@register.filter
def dget(d: Any, key: str):
    """
    Safe dict get.
    {{ some_dict|dget:"slug" }} -> "" si absent
    """
    try:
        if isinstance(d, dict):
            return d.get(key, "")
    except Exception:
        pass
    return ""


@register.filter
def in_namespaces(resolver_match: Any, ns: str) -> bool:
    """
    Safe: teste si un namespace est dans resolver_match.namespaces.
    Usage: {% if request.resolver_match|in_namespaces:"admin" %}
    """
    try:
        nss = getattr(resolver_match, "namespaces", None) or ()
        return ns in nss
    except Exception:
        return False


@register.filter
def app_label(obj: Any):
    """
    Retourne obj._meta.app_label de façon SAFE.
    """
    try:
        meta = getattr(obj, "_meta", None)
        return getattr(meta, "app_label", "") or ""
    except Exception:
        return ""


@register.filter
def model_name(obj: Any):
    """
    Retourne obj._meta.model_name de façon SAFE.
    """
    try:
        meta = getattr(obj, "_meta", None)
        return getattr(meta, "model_name", "") or ""
    except Exception:
        return ""


# -----------------------------
# Simple tags
# -----------------------------
@register.simple_tag
def dget_default(mapping: Any, key: str, default: Any = ""):
    """
    Safe dict get avec default.
    Usage:
      {% dget_default request.resolver_match.kwargs "slug" "" as current_slug %}
    """
    try:
        if isinstance(mapping, dict):
            return mapping.get(key, default)
    except Exception:
        pass
    return default


@register.simple_tag
def safe_url(url_name: str, *args, **kwargs) -> str:
    """
    Version SAFE de {% url %} :
    - retourne "" si NoReverseMatch
    Usage:
      {% safe_url "dashboard:hub" as url_hub %}
    """
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return ""
    except Exception:
        return ""


@register.simple_tag
def admin_change_url(obj: Any) -> str:
    """
    Retourne l'URL admin change d'un objet (ou "" si impossible).
    Usage:
      {% admin_change_url u as admin_change_url %}
    """
    if not obj:
        return ""
    try:
        meta = getattr(obj, "_meta", None)
        if not meta:
            return ""
        viewname = f"admin:{meta.app_label}_{meta.model_name}_change"
        return reverse(viewname, args=(obj.pk,))
    except NoReverseMatch:
        return ""
    except Exception:
        return ""






# # dashboard/templatetags/dashboard_tags.py
# from __future__ import annotations

# from typing import Any, Iterable, Optional

# from django import template
# from django.urls import NoReverseMatch, reverse

# register = template.Library()


# # -----------------------------
# # Filters
# # -----------------------------
# @register.filter
# def pluck(data: Any, key: str):
#     """
#     Extrait les valeurs associées à la clé 'key' depuis une liste de dict.
#     {{ data|pluck:"key" }}
#     """
#     if not isinstance(data, (list, tuple)):
#         return []
#     out = []
#     for item in data:
#         if isinstance(item, dict):
#             out.append(item.get(key))
#         else:
#             out.append(None)
#     return out


# @register.filter
# def dget(d: Any, key: str):
#     """
#     Safe dict get.
#     {{ some_dict|dget:"slug" }} -> "" si absent
#     """
#     try:
#         if isinstance(d, dict):
#             return d.get(key, "")
#     except Exception:
#         pass
#     return ""


# @register.filter
# def in_namespaces(resolver_match: Any, ns: str) -> bool:
#     """
#     Safe: teste si un namespace est dans resolver_match.namespaces.
#     Usage: {% if request.resolver_match|in_namespaces:"admin" %}
#     """
#     try:
#         nss = getattr(resolver_match, "namespaces", None) or ()
#         return ns in nss
#     except Exception:
#         return False


# # -----------------------------
# # Simple tags
# # -----------------------------
# @register.simple_tag
# def dget_default(mapping: Any, key: str, default: Any = ""):
#     """
#     Safe dict get avec default.
#     Usage:
#       {% dget_default request.resolver_match.kwargs "slug" "" as current_slug %}
#     """
#     try:
#         if isinstance(mapping, dict):
#             return mapping.get(key, default)
#     except Exception:
#         pass
#     return default


# @register.simple_tag
# def safe_url(viewname: str, *args, **kwargs) -> str:
#     """
#     Reverse safe: renvoie "" si NoReverseMatch.
#     Usage:
#       {% safe_url "dashboard:hub" as url_hub %}
#     """
#     try:
#         return reverse(viewname, args=args, kwargs=kwargs)
#     except Exception:
#         return ""


# @register.simple_tag
# def admin_change_url(obj: Any) -> str:
#     """
#     Retourne l'URL admin change d'un objet (ou "" si impossible).
#     Évite d'accéder à obj._meta dans le template (interdit).
#     Usage:
#       {% admin_change_url u as admin_change_url %}
#     """
#     if not obj:
#         return ""
#     try:
#         meta = getattr(obj, "_meta", None)
#         if not meta:
#             return ""
#         viewname = f"admin:{meta.app_label}_{meta.model_name}_change"
#         return reverse(viewname, args=(obj.pk,))
#     except NoReverseMatch:
#         return ""
#     except Exception:
#         return ""

# @register.filter
# def app_label(obj):
#     """
#     Retourne obj._meta.app_label de façon SAFE (sans exposer _meta dans le template).
#     """
#     try:
#         meta = getattr(obj, "_meta", None)
#         return getattr(meta, "app_label", "") or ""
#     except Exception:
#         return ""


# @register.filter
# def model_name(obj):
#     """
#     Retourne obj._meta.model_name de façon SAFE (sans exposer _meta dans le template).
#     """
#     try:
#         meta = getattr(obj, "_meta", None)
#         return getattr(meta, "model_name", "") or ""
#     except Exception:
#         return ""


# @register.simple_tag
# def safe_url(url_name: str, *args, **kwargs) -> str:
#     """
#     Version SAFE de {% url %} :
#     - retourne "" si NoReverseMatch
#     Usage:
#       {% safe_url "admin:app_model_change" u.pk as admin_change_url %}
#     """
#     try:
#         return reverse(url_name, args=args, kwargs=kwargs)
#     except NoReverseMatch:
#         return ""
#     except Exception:
#         return ""




# # dashboard/templatetags/dashboard_tags.py
# from __future__ import annotations

# from typing import Any, Iterable, List, Optional

# from django import template
# from django.utils.html import conditional_escape
# from django.utils.safestring import mark_safe

# register = template.Library()


# # -------------------------
# # Lists helpers
# # -------------------------
# @register.filter
# def pluck(data: Any, key: str) -> List[Any]:
#     """
#     Extrait les valeurs associées à la clé 'key' depuis une liste de dictionnaires.
#     Usage: {{ data|pluck:"key" }}
#     """
#     if not isinstance(data, (list, tuple)):
#         return []
#     out: List[Any] = []
#     for item in data:
#         if isinstance(item, dict):
#             out.append(item.get(key))
#         else:
#             out.append(None)
#     return out


# # -------------------------
# # Safe dict/attr getters
# # -------------------------
# @register.filter
# def dget(d: Any, key: str) -> Any:
#     """
#     Safe dict get:
#     {{ some_dict|dget:"slug" }} -> "" if missing
#     """
#     if isinstance(d, dict):
#         return d.get(key, "")
#     return ""


# @register.simple_tag
# def dget_default(obj: Any, key: str, default: Any = "") -> Any:
#     """
#     Safe getter dict/attr, avec valeur par défaut.
#     - dict: obj.get(key, default)
#     - objet: getattr(obj, key, default)
#     """
#     if obj is None:
#         return default
#     try:
#         if isinstance(obj, dict):
#             return obj.get(key, default)
#         return getattr(obj, key, default)
#     except Exception:
#         return default


# @register.simple_tag(takes_context=True)
# def rm_kwarg(context, key: str, default: Any = "") -> Any:
#     """
#     Récupère request.resolver_match.kwargs[key] de façon safe.
#     Usage: {% rm_kwarg "slug" "" as current_slug %}
#     """
#     request = context.get("request")
#     rm = getattr(request, "resolver_match", None) if request else None
#     kwargs = getattr(rm, "kwargs", None) if rm else None
#     if isinstance(kwargs, dict):
#         return kwargs.get(key, default)
#     return default


# @register.filter
# def attr(obj: Any, name: str) -> Any:
#     """
#     Safe getattr (sans underscore).
#     Usage: {{ obj|attr:"field_name" }}
#     """
#     if not obj or not name:
#         return ""
#     if str(name).startswith("_"):
#         return ""
#     try:
#         return getattr(obj, name, "")
#     except Exception:
#         return ""


# # -------------------------
# # Model meta helpers (évite u._meta)
# # -------------------------
# @register.filter
# def app_label(obj: Any) -> str:
#     """
#     Retourne le app_label d'un modèle (sans u._meta dans template).
#     Usage: {{ u|app_label }}
#     """
#     try:
#         meta = getattr(obj, "_meta", None)
#         return getattr(meta, "app_label", "") or ""
#     except Exception:
#         return ""


# @register.filter
# def model_name(obj: Any) -> str:
#     """
#     Retourne le model_name d'un modèle (sans u._meta dans template).
#     Usage: {{ u|model_name }}
#     """
#     try:
#         meta = getattr(obj, "_meta", None)
#         return getattr(meta, "model_name", "") or ""
#     except Exception:
#         return ""


# # -------------------------
# # Optional: safe join for namespaces etc.
# # -------------------------
# @register.filter
# def to_list(value: Any) -> List[Any]:
#     """
#     Convertit tuple/set/iterable en list, sinon [].
#     """
#     if value is None:
#         return []
#     if isinstance(value, list):
#         return value
#     if isinstance(value, (tuple, set)):
#         return list(value)
#     return [value]







# # dashboard/templatetags/dashboard_tags.py
# from __future__ import annotations

# from typing import Any, Iterable, List, Optional

# from django import template

# register = template.Library()


# @register.filter(name="pluck")
# def pluck(data: Any, key: str) -> List[Any]:
#     """
#     Extrait les valeurs associées à 'key' depuis une liste/tuple/iterable de dicts/objets.

#     Usage template:
#       {{ data|pluck:"key" }}
#       - si item est dict => item.get(key)
#       - sinon => getattr(item, key, None)

#     Retourne toujours une liste (jamais exception).
#     """
#     if not data:
#         return []

#     # Supporte list/tuple/queryset/itérables
#     if not isinstance(data, (list, tuple)):
#         try:
#             data = list(data)  # type: ignore[arg-type]
#         except Exception:
#             return []

#     out: List[Any] = []
#     for item in data:
#         if item is None:
#             out.append(None)
#             continue

#         # dict
#         if isinstance(item, dict):
#             out.append(item.get(key))
#             continue

#         # objet
#         try:
#             out.append(getattr(item, key, None))
#         except Exception:
#             out.append(None)

#     return out


# @register.filter(name="dget")
# def dget(d: Any, key: str) -> Any:
#     """
#     Safe get pour templates (silencieux, pas de failed lookup).

#     - si d est dict => d.get(key, "")
#     - sinon => getattr(d, key, "")
#     - si erreur => ""

#     Usage:
#       {{ rm.kwargs|dget:"slug" }}
#       {{ some_dict|dget:"name" }}
#     """
#     if d is None or key is None:
#         return ""

#     try:
#         if isinstance(d, dict):
#             return d.get(key, "")
#     except Exception:
#         return ""

#     try:
#         return getattr(d, key, "")
#     except Exception:
#         return ""


# @register.simple_tag(name="dget_default")
# def dget_default(d: Any, key: str, default: Any = "") -> Any:
#     """
#     Version tag (pas filter) avec default paramétrable.

#     Usage:
#       {% dget_default rm.kwargs "slug" "" as current_slug %}
#       {% dget_default some_dict "title" "—" as title %}
#     """
#     if d is None or key is None:
#         return default

#     try:
#         if isinstance(d, dict):
#             val = d.get(key, default)
#             return default if val is None else val
#     except Exception:
#         return default

#     try:
#         val = getattr(d, key, default)
#         return default if val is None else val
#     except Exception:
#         return default


# @register.filter(name="tget")
# def tget(obj: Any, attr: str) -> Any:
#     """
#     Safe getattr:
#       {{ user|tget:"email" }}
#     """
#     if obj is None or not attr:
#         return ""
#     try:
#         return getattr(obj, attr, "")
#     except Exception:
#         return ""


# @register.filter(name="hasattr")
# def hasattr_filter(obj: Any, attr: str) -> bool:
#     """
#     Safe hasattr pour templates:
#       {% if profile|hasattr:"status" %}...{% endif %}
#     """
#     if obj is None or not attr:
#         return False
#     try:
#         return hasattr(obj, attr)
#     except Exception:
#         return False





# # dashboard/templatetags/dashboard_tags.py
# from __future__ import annotations

# from django import template

# register = template.Library()

# @register.filter
# def pluck(data, key):
#     """
#     Extrait les valeurs associées à la clé 'key' depuis une liste de dictionnaires.
#     Usage dans un template : {{ data|pluck:"key" }}
#     """
#     if not isinstance(data, (list, tuple)):
#         return []
    
#     results = []
#     for item in data:
#         if isinstance(item, dict) and key in item:
#             results.append(item[key])
#         else:
#             results.append(None)  # Ajoute None si la clé est absente

#     return results

# @register.filter
# def dget(d: object, key: str):
#     """
#     Safe dict get for templates:
#     {{ some_dict|dget:"slug" }} -> "" if missing (no noisy failed lookup)
#     """
#     try:
#         if isinstance(d, dict):
#             return d.get(key, "")
#     except Exception:
#         pass
#     return ""