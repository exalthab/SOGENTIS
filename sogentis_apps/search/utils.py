import re
from django.db.models import Q
from django.utils.safestring import mark_safe
from social.models import Project, Publication, Engagement


def perform_search(query):
    """Recherche multi-modèles dans l'app social"""
    return {
        "projects": Project.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
        "publications": Publication.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
        "engagements": Engagement.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
    }


def highlight_text(text, query):
    """Met en évidence le mot recherché"""
    regex = re.compile(re.escape(query), re.IGNORECASE)
    return mark_safe(regex.sub(r'<mark class="live-hl">\g<0></mark>', text))


def format_search_results(data, query=None, limit=5):
    """Transforme les objets en dictionnaire pour l'affichage"""
    results = []

    for p in data["projects"][:limit]:
        title = highlight_text(p.title, query) if query else p.title
        results.append({"type": "projet", "title": title, "url": getattr(p, "get_absolute_url", lambda: "#")()})

    for pub in data["publications"][:limit]:
        title = highlight_text(pub.title, query) if query else pub.title
        results.append({"type": "publication", "title": title, "url": getattr(pub, "get_absolute_url", lambda: "#")()})

    for eng in data["engagements"][:limit]:
        title = highlight_text(eng.title, query) if query else eng.title
        results.append({"type": "engagement", "title": title, "url": getattr(eng, "get_absolute_url", lambda: "#")()})

    return results
