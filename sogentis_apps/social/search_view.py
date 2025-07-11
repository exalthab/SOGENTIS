from django.shortcuts import render
from django.db.models import Q
from .models import Project, Publication, Engagement, Donation
# from .models import Don  # Active si tu utilises ce modèle séparé

def search_view(request):
    query = request.GET.get("q", "").strip()

    project_results = Project.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else []

    publication_results = Publication.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    ) if query else []

    engagement_results = Engagement.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else []

    donation_results = Donation.objects.filter(
        Q(donor_name__icontains=query) | Q(message__icontains=query)
    ) if query else []

    # Si tu as un modèle Don distinct, décommente et adapte le champ :
    # don_results = Don.objects.filter(Q(montant__icontains=query)) if query else []

    # Pour savoir s'il y a des résultats (convertir en list pour any sur queryset)
    has_results = any([
        bool(project_results),
        bool(publication_results),
        bool(engagement_results),
        bool(donation_results),
        # bool(don_results),
    ])

    return render(request, "social/search_results.html", {
        "query": query,
        "project_results": project_results,
        "publication_results": publication_results,
        "engagement_results": engagement_results,
        "donation_results": donation_results,
        # "don_results": don_results,
        "has_results": has_results,
    })