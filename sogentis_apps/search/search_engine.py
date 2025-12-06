"""
Fonctions utilitaires de recherche.

- search_index_simple : recherche simple par icontains sur IndexedDocument.
- search_index_postgres : si tu utilises Postgres et django.contrib.postgres,
  fait une recherche full-text (SearchVector).
"""
from django.db.models import Q
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from .models import IndexedDocument

def search_index_simple(q):
    """
    Recherche simple : cherche q dans title, description, body, file_url, author username.
    Retourne queryset d'IndexedDocument.
    """
    if not q:
        return IndexedDocument.objects.none()

    qs = IndexedDocument.objects.filter(
        Q(title__icontains=q) |
        Q(description__icontains=q) |
        Q(body__icontains=q) |
        Q(file_url__icontains=q) |
        Q(author__username__icontains=q)
    ).distinct()

    return qs.order_by("-created_at")


def search_index(q):
    """
    Choisit la meilleure méthode disponible (Postgres full-text si possible,
    sinon fallback sur la recherche simple).
    """
    try:
        # tentative d'import Postgres Search
        from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
        vector = SearchVector("title", weight="A") + SearchVector("description", weight="B") + SearchVector("body", weight="C")
        query = SearchQuery(q)
        qs = IndexedDocument.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.01).order_by("-rank")
        return qs
    except Exception as e:
        logger.debug("Postgres full-text not available, fallback to simple search: %s", e)
        return search_index_simple(q)
