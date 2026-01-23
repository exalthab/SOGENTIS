# search/urls.py
from django.urls import path
from .views import search_view, ajax_search, reindex_view

app_name = "search"

urlpatterns = [
    path("", search_view, name="search"),
    path("ajax/", ajax_search, name="ajax_search"),
    path("reindex/", reindex_view, name="reindex"),
]






# from django.urls import path
# from search.views import search_view, ajax_search

# app_name = "search"

# urlpatterns = [
#     path("", search_view, name="search"),
#     path("ajax/", ajax_search, name="ajax_search"),
# ]
