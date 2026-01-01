# economic/ecommerce/views/search.py
from .index import _catalog_view


def ecommerce_search_view(request):
    """
    URL:
      path("search/", ecommerce_search_view, name="search")
    """
    return _catalog_view(request, "economic/ecommerce/search.html")




# # ecommerce/views/search.py
# from django.shortcuts import render

# def search_view(request):
#     query = request.GET.get("q", "")
#     return render(request, "economic/ecommerce/search.html", {"query": query})
