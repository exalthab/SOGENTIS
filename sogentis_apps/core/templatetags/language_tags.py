# -----------------------------
# File: core/templatetags/language_tags.py
# -----------------------------
from django import template
from django.conf.locale import LANG_INFO

register = template.Library()

@register.simple_tag
def get_lang_info(code, key="name_local"):
    """
    Retourne une information sur la langue identifiée par `code`.

    - `code` : code de la langue (ex: 'de', 'fr', 'wo')
    - `key`  : champ à retourner (par défaut 'name_local').

    Exemple : {% get_lang_info 'de' %} -> 'Deutsch'
    Exemple : {% get_lang_info 'fr' 'name' %} -> 'French' (si disponible)
    """
    return LANG_INFO.get(code, {}).get(key, code)


@register.simple_tag
def get_all_langs():
    """
    Retourne la structure LANG_INFO filtrée et ordonnée pour usage éventuel
    dans les templates (utile si tu veux boucler sur les langues avec plus
    d'informations).

    Exemple d'usage dans un template :
      {% for code, info in get_all_langs.items %}
        {{ code }} - {{ info.name_local }}
      {% endfor %}
    """
    # convertit LANG_INFO (dict) en un dict simple trié par code
    return {k: v for k, v in sorted(LANG_INFO.items())}
