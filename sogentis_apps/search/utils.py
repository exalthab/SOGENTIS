# search/utils.py
from django.apps import apps

TYPE_MAP = {
    "social.project": "projects",
    "social.publication": "publications",   # ✅ payant
    "social.engagement": "engagements",
    "social.document": "documents",         # ✅ gratuit
}

PAID_KEYS = {"social.publication"}  # tout ce qui est payant / protégé

def indexed_type(item) -> str:
    key = f"{item.source_app}.{item.source_model}"
    return TYPE_MAP.get(key, "other")


def resolve_indexed_url(item) -> str:
    """
    IMPORTANT:
    - Pour les modèles payants (Publication), on retourne uniquement la page détail (paywall),
      JAMAIS file_url.
    - Pour les docs gratuits, on peut fallback sur file_url si pas de page.
    """
    key = f"{item.source_app}.{item.source_model}"

    try:
        Model = apps.get_model(item.source_app, item.source_model)
        obj = Model.objects.filter(pk=item.object_id).first()
        if obj and hasattr(obj, "get_absolute_url"):
            url = obj.get_absolute_url()
            if url:
                return url
    except Exception:
        obj = None

    # 🔒 Payant : pas de lien direct fichier
    if key in PAID_KEYS:
        return "#"

    # ✅ Gratuit : fallback possible vers file_url
    return item.file_url or "#"







# # search/utils.py
# import re
# from django.db.models import Q
# from django.utils.safestring import mark_safe
# from social.models import Project, Publication, Engagement


# def perform_search(query):
#     """Recherche multi-modèles dans l'app social"""
#     return {
#         "projects": Project.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
#         "publications": Publication.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
#         "engagements": Engagement.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
#     }


# def highlight_text(text, query):
#     """Met en évidence le mot recherché"""
#     regex = re.compile(re.escape(query), re.IGNORECASE)
#     return mark_safe(regex.sub(r'<mark class="live-hl">\g<0></mark>', text))


# def format_search_results(data, query=None, limit=5):
#     """Transforme les objets en dictionnaire pour l'affichage"""
#     results = []

#     for p in data["projects"][:limit]:
#         title = highlight_text(p.title, query) if query else p.title
#         results.append({"type": "projet", "title": title, "url": getattr(p, "get_absolute_url", lambda: "#")()})

#     for pub in data["publications"][:limit]:
#         title = highlight_text(pub.title, query) if query else pub.title
#         results.append({"type": "publication", "title": title, "url": getattr(pub, "get_absolute_url", lambda: "#")()})

#     for eng in data["engagements"][:limit]:
#         title = highlight_text(eng.title, query) if query else eng.title
#         results.append({"type": "engagement", "title": title, "url": getattr(eng, "get_absolute_url", lambda: "#")()})

#     return results
