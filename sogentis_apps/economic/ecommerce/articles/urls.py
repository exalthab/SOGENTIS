# economic/ecommerce/articles/urls.py
from django.urls import path
from economic.ecommerce.articles.views import article_list_view, article_detail_view


urlpatterns = [
    path("", article_list_view, name="list"),
    path("<slug:slug>/", article_detail_view, name="detail"),
]