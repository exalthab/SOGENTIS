# import re
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.utils.safestring import mark_safe
# from django.utils.translation import gettext_lazy as _
# from .models import Project, Publication, Engagement

# # 🔎 Fonction de recherche multi-modèles
# def perform_search(query):
#     projects = Project.objects.filter(title__icontains=query) | Project.objects.filter(description__icontains=query)
#     publications = Publication.objects.filter(title__icontains=query) | Publication.objects.filter(description__icontains=query)
#     engagements = Engagement.objects.filter(title__icontains=query) | Engagement.objects.filter(description__icontains=query)
#     return {
#         "projects": projects,
#         "publications": publications,
#         "engagements": engagements,
#     }

# # 🌐 Recherche AJAX pour live search
# def ajax_search(request):
#     query = request.GET.get("q", "").strip()
#     if not query:
#         return JsonResponse({"results": []})

#     results = []
#     data = perform_search(query)

#     def highlight(text):
#         regex = re.compile(re.escape(query), re.IGNORECASE)
#         return mark_safe(regex.sub(r'<mark class="live-hl">\g<0></mark>', text))

#     # Normalisation des résultats
#     for p in data["projects"][:5]:
#         results.append({
#             "type": "projet",
#             "title": highlight(p.title),
#             "url": getattr(p, "get_absolute_url", lambda: "#")(),
#         })

#     for pub in data["publications"][:5]:
#         results.append({
#             "type": "publication",
#             "title": highlight(pub.title),
#             "url": getattr(pub, "get_absolute_url", lambda: "#")(),
#         })

#     for eng in data["engagements"][:5]:
#         results.append({
#             "type": "engagement",
#             "title": highlight(eng.title),
#             "url": getattr(eng, "get_absolute_url", lambda: "#")(),
#         })

#     return JsonResponse({"results": results})

# # 🔍 Recherche classique (page complète)
# def search_view(request):
#     query = request.GET.get("q", "").strip()
#     context = {
#         "query": query,
#         "results": [],
#         "section_menu": "core/partials/_menu_soci.html"
#     }

#     if query:
#         try:
#             search_data = perform_search(query)
#             # On fusionne les résultats pour la page classique
#             results = []
#             for item in search_data["projects"]:
#                 results.append({"type": "projet", "title": item.title, "url": getattr(item, "get_absolute_url", lambda: "#")()})
#             for item in search_data["publications"]:
#                 results.append({"type": "publication", "title": item.title, "url": getattr(item, "get_absolute_url", lambda: "#")()})
#             for item in search_data["engagements"]:
#                 results.append({"type": "engagement", "title": item.title, "url": getattr(item, "get_absolute_url", lambda: "#")()})
            
#             context["results"] = results
#         except Exception:
#             context["error"] = _("Une erreur est survenue pendant la recherche.")
#     else:
#         context["message"] = _("Veuillez entrer un mot-clé de recherche.")

#     return render(request, "social/search_results.html", context)





# import re
# from django.core.paginator import Paginator
# from django.shortcuts import render
# from django.utils.safestring import mark_safe

# from .models import Project, Publication, Engagement   # <-- À adapter à ton app


# # --- Highlight function ---
# def highlight(text, query):
#     if not text or not query:
#         return text
    
#     regex = re.compile(re.escape(query), re.IGNORECASE)
#     return mark_safe(
#         regex.sub(r'<mark class="search-highlight">\g<0></mark>', text)
#     )


# # --- Main search view ---
# def search(request):
#     query = request.GET.get("q", "").strip()
#     type_filter = request.GET.get("type")

#     # If no query → empty results
#     if not query:
#         return render(request, "search_results.html", {
#             "query": "",
#             "results": [],
#             "total_results": 0,
#         })

#     # 1️⃣ FETCH DATA FROM MODELS
#     projects = Project.objects.filter(title__icontains=query) | \
#                Project.objects.filter(description__icontains=query)

#     publications = Publication.objects.filter(title__icontains=query) | \
#                    Publication.objects.filter(content__icontains=query)

#     engagements = Engagement.objects.filter(title__icontains=query) | \
#                   Engagement.objects.filter(description__icontains=query)

#     # 2️⃣ NORMALIZE RESULTS INTO A SINGLE LIST
#     results = []

#     # --- Projects ---
#     for p in projects:
#         results.append({
#             "type": "project",
#             "title": highlight(p.title, query),
#             "snippet": highlight(p.description, query),
#             "url": p.get_absolute_url(),
#         })

#     # --- Publications ---
#     for pub in publications:
#         results.append({
#             "type": "publication",
#             "title": highlight(pub.title, query),
#             "snippet": highlight(pub.content, query),
#             "url": getattr(pub, "get_absolute_url", lambda: None)(),
#         })

#     # --- Engagements ---
#     for eng in engagements:
#         results.append({
#             "type": "engagement",
#             "title": highlight(eng.title, query),
#             "snippet": highlight(eng.description, query),
#             "url": getattr(eng, "get_absolute_url", lambda: None)(),
#         })

#     # 3️⃣ OPTIONAL FILTERING (sidebar)
#     if type_filter:
#         results = [r for r in results if r["type"] == type_filter]

#     # 4️⃣ PAGINATION (PROFESSIONNELLE)
#     paginator = Paginator(results, 15)  # 15 résultats par page
#     page = request.GET.get("page")
#     page_obj = paginator.get_page(page)

#     # 5️⃣ CONTEXT
#     context = {
#         "query": query,
#         "results": page_obj,
#         "total_results": len(results),
#         "type": type_filter,
#         "is_paginated": page_obj.has_other_pages(),
#         "page_obj": page_obj,
#         "paginator": paginator,
#     }

#     return render(request, "search_results.html", context)








# from django.shortcuts import render
# from django.db.models import Q
# from .models import Project, Publication, Engagement, Donation
# # from .models import Don  # Active si tu utilises ce modèle séparé

# def search_view(request):
#     query = request.GET.get("q", "").strip()

#     project_results = Project.objects.filter(
#         Q(title__icontains=query) | Q(description__icontains=query)
#     ) if query else []

#     publication_results = Publication.objects.filter(
#         Q(title__icontains=query) | Q(content__icontains=query)
#     ) if query else []

#     engagement_results = Engagement.objects.filter(
#         Q(title__icontains=query) | Q(description__icontains=query)
#     ) if query else []

#     donation_results = Donation.objects.filter(
#         Q(donor_name__icontains=query) | Q(message__icontains=query)
#     ) if query else []

#     # Si tu as un modèle Don distinct, décommente et adapte le champ :
#     # don_results = Don.objects.filter(Q(montant__icontains=query)) if query else []

#     # Pour savoir s'il y a des résultats (convertir en list pour any sur queryset)
#     has_results = any([
#         bool(project_results),
#         bool(publication_results),
#         bool(engagement_results),
#         bool(donation_results),
#         # bool(don_results),
#     ])

#     return render(request, "social/search_results.html", {
#         "query": query,
#         "project_results": project_results,
#         "publication_results": publication_results,
#         "engagement_results": engagement_results,
#         "donation_results": donation_results,
#         # "don_results": don_results,
#         "has_results": has_results,
#     })