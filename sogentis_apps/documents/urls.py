# #/documents/urls.py
# from django.urls import path
# from . import views
# from .views import ToggleDocumentVisibilityView


# app_name = "documents"

# urlpatterns = [
#     path("", views.DocumentListView.as_view(), name="list"),
#     path("new/", views.DocumentCreateView.as_view(), name="create"),
#     path("archived/", views.DocumentArchiveView.as_view(), name="archived"),
#     path("<int:pk>/", views.DocumentDetailView.as_view(), name="detail"),
#     path("<int:pk>/toggle-visibility/", ToggleDocumentVisibilityView.as_view(), name="toggle_visibility"),
#     path("search/", views.search_documents, name="search"),


# ]
