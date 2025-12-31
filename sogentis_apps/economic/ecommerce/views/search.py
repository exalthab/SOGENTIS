# ecommerce/views/search.py
from django.shortcuts import render

def search_view(request):
    query = request.GET.get("q", "")
    return render(request, "economic/ecommerce/search.html", {"query": query})
