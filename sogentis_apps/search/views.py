from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import re

from social.models import Project, Publication, Engagement
from documents.models import Document


# -----------------------------------------------------------
#  Fonction utilitaire : surbrillance
# -----------------------------------------------------------
def highlight(text, query):
    if not text:
        return text
    regex = re.compile(re.escape(query), re.IGNORECASE)
    return mark_safe(regex.sub(r'<mark class="live-hl">\g<0></mark>', text))


# -----------------------------------------------------------
#  Fonction de recherche globale (multi-app)
# -----------------------------------------------------------
def perform_search(query):
    return {
        "projects": Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ),
        "publications": Publication.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ),
        "engagements": Engagement.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ),
        "documents": Document.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ),
    }


# -----------------------------------------------------------
#  Recherche AJAX (live search)
# -----------------------------------------------------------
def ajax_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    data = perform_search(query)
    results = []

    def add_items(qs, label):
        for obj in qs[:5]:
            results.append({
                "type": label,
                "title": highlight(obj.title, query),
                "url": getattr(obj, "get_absolute_url", lambda: "#")(),
            })

    add_items(data["projects"], "projet")
    add_items(data["publications"], "publication")
    add_items(data["engagements"], "engagement")
    add_items(data["documents"], "document")

    return JsonResponse({"results": results})


# -----------------------------------------------------------
#  Recherche classique (page de résultats)
# -----------------------------------------------------------
def search_view(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return render(request, "search/search_results.html", {
            "query": "",
            "results": [],
            "message": _("Veuillez entrer un mot-clé."),
        })

    try:
        data = perform_search(query)
        results = []

        # Normalisation pour template
        for label, items in data.items():
            for obj in items:
                results.append({
                    "type": label,
                    "title": obj.title,
                    "snippet": getattr(obj, "description", None),
                    "url": getattr(obj, "get_absolute_url", lambda: "#")(),
                })

    except Exception:
        return render(request, "search/search_results.html", {
            "query": query,
            "results": [],
            "error": _("Une erreur est survenue."),
        })

    return render(request, "search/search_results.html", {
        "query": query,
        "results": results,
    })
