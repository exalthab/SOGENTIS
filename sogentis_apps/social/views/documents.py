import re
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from social.models import Project, Publication, Engagement  # On cherche dans Social
from django.utils.translation import gettext as _

def perform_search(query):
    """
    Fonction utilitaire pour rechercher dans différents modèles.
    """
    results = {
        "projects": Project.objects.filter(title__icontains=query),
        "publications": Publication.objects.filter(title__icontains=query),
        "engagements": Engagement.objects.filter(title__icontains=query),
    }
    return results


# 🔍 Recherche classique (page complète)
def search(request):
    query = request.GET.get("q", "").strip()
    context = {
        "query": query,
        "results": [],
        "section_menu": "core/partials/_menu_soci.html"
    }

    if query:
        try:
            search_data = perform_search(query)
            results = []
            for item in search_data["projects"]:
                results.append({
                    "type": "projet",
                    "title": item.title,
                    "url": getattr(item, "get_absolute_url", lambda: "#")()
                })
            for item in search_data["publications"]:
                results.append({
                    "type": "publication",
                    "title": item.title,
                    "url": getattr(item, "get_absolute_url", lambda: "#")()
                })
            for item in search_data["engagements"]:
                results.append({
                    "type": "engagement",
                    "title": item.title,
                    "url": getattr(item, "get_absolute_url", lambda: "#")()
                })
            context["results"] = results
        except Exception:
            context["error"] = _("Une erreur est survenue pendant la recherche.")
    else:
        context["message"] = _("Veuillez entrer un mot-clé de recherche.")

    return render(request, "documents/search_results.html", context)


# 🌐 Recherche AJAX pour live search
def ajax_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    data = perform_search(query)
    results = []

    def highlight(text):
        regex = re.compile(re.escape(query), re.IGNORECASE)
        return mark_safe(regex.sub(r'<mark class="live-hl">\g<0></mark>', text))

    for p in data["projects"][:5]:
        results.append({"type": "projet", "title": highlight(p.title), "url": getattr(p, "get_absolute_url", lambda: "#")()})
    for pub in data["publications"][:5]:
        results.append({"type": "publication", "title": highlight(pub.title), "url": getattr(pub, "get_absolute_url", lambda: "#")()})
    for eng in data["engagements"][:5]:
        results.append({"type": "engagement", "title": highlight(eng.title), "url": getattr(eng, "get_absolute_url", lambda: "#")()})

    return JsonResponse({"results": results})
