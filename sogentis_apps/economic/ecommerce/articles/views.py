# economic/ecommerce/articles/views.py
from django.shortcuts import render, get_object_or_404

from economic.ecommerce.articles.models import Article

def article_list_view(request):
    articles = Article.objects.filter(is_published=True)

    context = {
        "articles": articles,
    }

    return render(
        request,
        "economic/ecommerce/articles/article_list.html",
        context,
    )


def article_detail_view(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
    )

    context = {
        "article": article,
    }

    return render(
        request,
        "economic/ecommerce/articles/article_detail.html",
        context,
    )
