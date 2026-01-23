# search/views.py
from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from .models import IndexedDocument
from .search_engine import search_index

# --- Mapping type (pour coller au template) ---
TYPE_MAP = {
    "social.project": "projects",
    "social.publication": "publications",   # 🔒 payant
    "social.engagement": "engagements",
    "social.document": "documents",         # ✅ gratuit
}

PAID_KEYS = {"social.publication"}  # tout ce qui doit rester protégé


def _indexed_key(item: IndexedDocument) -> str:
    return f"{item.source_app}.{item.source_model}"


def indexed_type(item: IndexedDocument) -> str:
    return TYPE_MAP.get(_indexed_key(item), "other")


def indexed_access(item: IndexedDocument) -> str:
    """
    Retourne 'paid' ou 'free' selon le modèle source.
    (Tu peux étendre plus tard selon un champ price sur Publication.)
    """
    t = indexed_type(item)
    if t == "publications":
        return "paid"
    if t == "documents":
        return "free"
    return ""


def resolve_indexed_url(item: IndexedDocument) -> str:
    """
    IMPORTANT SECURITE :
    - Publication (payant) : renvoyer uniquement get_absolute_url (page paywall),
      JAMAIS file_url (sinon bypass paiement).
    - Document (gratuit) : fallback possible vers file_url.
    """
    key = _indexed_key(item)

    # 1) Essayer get_absolute_url sur l'objet source
    try:
        from django.apps import apps

        Model = apps.get_model(item.source_app, item.source_model)
        obj = Model.objects.filter(pk=item.object_id).first()
        if obj and hasattr(obj, "get_absolute_url"):
            url = obj.get_absolute_url()
            if url:
                return url
    except Exception:
        obj = None

    # 2) Payant -> jamais de lien direct fichier
    if key in PAID_KEYS:
        return "#"

    # 3) Gratuit -> fallback file_url possible
    return item.file_url or "#"


def ajax_search(request):
    """
    Live search (JSON). Renvoie les mêmes 'type' que le template.
    """
    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"results": []})

    qs = search_index(q)[:8]

    results = []
    for item in qs:
        results.append(
            {
                "type": indexed_type(item),
                "access": indexed_access(item),
                "title": item.title or "",
                "url": resolve_indexed_url(item),
            }
        )

    return JsonResponse({"results": results})


def search_view(request):
    """
    Page résultats : templates/search/search_results.html
    """
    q = (request.GET.get("q") or "").strip()

    if not q:
        return render(
            request,
            "search/search_results.html",
            {
                "query": "",
                "results": [],
                "message": _("Veuillez entrer un mot-clé."),
            },
        )

    qs = search_index(q)[:60]

    results = []
    for item in qs:
        snippet = item.description or (item.body[:160] if item.body else "")
        results.append(
            {
                "type": indexed_type(item),          # projects/publications/...
                "access": indexed_access(item),      # free/paid
                "title": item.title,
                "snippet": snippet,
                "url": resolve_indexed_url(item),    # sécurisé
            }
        )

    return render(
        request,
        "search/search_results.html",
        {"query": q, "results": results},
    )


@staff_member_required
def reindex_view(request):
    """
    Reconstruit IndexedDocument depuis les modèles sources.
    Template : templates/search/reindex_result.html
    """
    # Supprime l'index existant
    IndexedDocument.objects.all().delete()

    sources = [
        ("social", "Document"),
        ("social", "Publication"),
        ("social", "Project"),
        ("social", "Engagement"),
    ]

    created = 0
    skipped = 0

    from django.apps import apps
    from .signals import _index_instance  # on réutilise la logique d'indexation

    for app_label, model_name in sources:
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            skipped += 1
            continue

        for obj in Model.objects.all().iterator():
            _index_instance(Model, obj)  # sender=Model (classe)
            created += 1

    return render(
        request,
        "search/reindex_result.html",
        {"message": f"Reindex terminé. Objets traités: {created}. Sources ignorées: {skipped}."},
    )






# # search/views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db.models import Q
# from django.utils.safestring import mark_safe
# from django.utils.translation import gettext_lazy as _
# import re

# from social.models import Project, Publication, Engagement
# from documents.models import Document


# # -----------------------------------------------------------
# #  Fonction utilitaire : surbrillance
# # -----------------------------------------------------------
# def highlight(text, query):
#     if not text:
#         return text
#     regex = re.compile(re.escape(query), re.IGNORECASE)
#     return mark_safe(regex.sub(r'<mark class="live-hl">\g<0></mark>', text))


# # -----------------------------------------------------------
# #  Fonction de recherche globale (multi-app)
# # -----------------------------------------------------------
# def perform_search(query):
#     return {
#         "projects": Project.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         ),
#         "publications": Publication.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         ),
#         "engagements": Engagement.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         ),
#         "documents": Document.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         ),
#     }


# # -----------------------------------------------------------
# #  Recherche AJAX (live search)
# # -----------------------------------------------------------
# def ajax_search(request):
#     query = request.GET.get("q", "").strip()
#     if not query:
#         return JsonResponse({"results": []})

#     data = perform_search(query)
#     results = []

#     def add_items(qs, label):
#         for obj in qs[:5]:
#             results.append({
#                 "type": label,
#                 "title": highlight(obj.title, query),
#                 "url": getattr(obj, "get_absolute_url", lambda: "#")(),
#             })

#     add_items(data["projects"], "projet")
#     add_items(data["publications"], "publication")
#     add_items(data["engagements"], "engagement")
#     add_items(data["documents"], "document")

#     return JsonResponse({"results": results})


# # -----------------------------------------------------------
# #  Recherche classique (page de résultats)
# # -----------------------------------------------------------
# def search_view(request):
#     query = request.GET.get("q", "").strip()

#     if not query:
#         return render(request, "search/search_results.html", {
#             "query": "",
#             "results": [],
#             "message": _("Veuillez entrer un mot-clé."),
#         })

#     try:
#         data = perform_search(query)
#         results = []

#         # Normalisation pour template
#         for label, items in data.items():
#             for obj in items:
#                 results.append({
#                     "type": label,
#                     "title": obj.title,
#                     "snippet": getattr(obj, "description", None),
#                     "url": getattr(obj, "get_absolute_url", lambda: "#")(),
#                 })

#     except Exception:
#         return render(request, "search/search_results.html", {
#             "query": query,
#             "results": [],
#             "error": _("Une erreur est survenue."),
#         })

#     return render(request, "search/search_results.html", {
#         "query": query,
#         "results": results,
#     })
