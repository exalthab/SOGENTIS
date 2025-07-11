# dashboard/templatetags/dashboard_tags.py

from django import template

register = template.Library()

@register.filter
def pluck(data, key):
    """
    Extrait les valeurs associées à la clé 'key' depuis une liste de dictionnaires.
    Usage dans un template : {{ data|pluck:"key" }}
    """
    if not isinstance(data, (list, tuple)):
        return []
    
    results = []
    for item in data:
        if isinstance(item, dict) and key in item:
            results.append(item[key])
        else:
            results.append(None)  # Ajoute None si la clé est absente

    return results
