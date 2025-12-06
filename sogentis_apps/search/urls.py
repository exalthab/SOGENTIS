from django.urls import path
from search.views import search_view, ajax_search

app_name = "search"

urlpatterns = [
    path("", search_view, name="search"),
    path("ajax/", ajax_search, name="ajax_search"),
]
