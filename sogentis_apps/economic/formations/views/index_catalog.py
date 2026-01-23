# economic/formations/views/index_catalog.py
from __future__ import annotations

from django.shortcuts import render
from django.utils.translation import get_language

from ..models import CourseCategory, Course


def formations_index_view(request):
    lang = get_language() or "fr"

    categories = (
        CourseCategory.objects.filter(is_active=True)
        .filter(translations__language_code=lang)
        .order_by("order", "id")
        .distinct()[:12]
    )

    featured_courses = (
        Course.objects.filter(is_active=True, is_featured=True)
        .filter(translations__language_code=lang)
        .select_related("category")
        .order_by("-published_at", "-created_at")
        .distinct()[:9]
    )

    return render(
        request,
        "economic/formations/index.html",
        {
            "categories": categories,
            "featured_courses": featured_courses,
        },
    )






# # economic/formations/views/index_catalog.py
# from __future__ import annotations

# from django.shortcuts import render
# from django.utils.translation import get_language

# from ..models import CourseCategory, Course


# def _parler_filter_lang(qs, lang: str):
#     """
#     Rend un queryset parler 'lang-aware' sans casser si `.language()` n'existe pas.
#     Priorité:
#     1) qs.language(lang)      (si manager parler)
#     2) qs.active_translations(lang) (parler)
#     3) fallback SQL: translations__language_code=lang
#     """
#     if hasattr(qs, "language"):
#         try:
#             return qs.language(lang)
#         except Exception:
#             pass

#     if hasattr(qs, "active_translations"):
#         try:
#             return qs.active_translations(lang)
#         except Exception:
#             pass

#     # fallback stable: filtre sur la table translations
#     return qs.filter(translations__language_code=lang).distinct()


# def formations_index_view(request):
#     lang = (get_language() or "fr").split("-")[0]  # "fr-fr" -> "fr"

#     categories_qs = CourseCategory.objects.filter(is_active=True).order_by("order", "id")
#     courses_qs = Course.objects.filter(is_active=True).select_related("category")

#     # ✅ language-aware sans casser
#     categories = _parler_filter_lang(categories_qs, lang)[:12]
#     featured_courses = (
#         _parler_filter_lang(courses_qs.filter(is_featured=True), lang)
#         .order_by("-published_at", "-created_at")[:9]
#     )

#     return render(
#         request,
#         "economic/formations/index.html",
#         {
#             "lang": lang,
#             "categories": categories,
#             "featured_courses": featured_courses,
#         },
#     )






# # economic/formations/views/index_catalog.py

# from django.shortcuts import render
# from django.utils.translation import get_language
# from ..models.course import Course, CourseCategory


# def formations_index_view(request):
#     lang = get_language()

#     courses = Course.objects.filter(is_active=True)
#     return render(request, "economic/formations/index.html", {"courses": courses})
# from django.shortcuts import render
# from django.utils.translation import get_language

# from ..models import CourseCategory, Course


# def formations_index_view(request):
#     lang = get_language()

#     categories = CourseCategory.objects.filter(is_active=True).language(lang).order_by("order", "id")[:12]
#     featured_courses = (
#         Course.objects.filter(is_active=True, is_featured=True)
#         .language(lang)
#         .select_related("category")
#         .order_by("-published_at", "-created_at")[:9]
#     )

#     return render(request, "economic/formations/index.html", {
#         "categories": categories,
#         "featured_courses": featured_courses,
#     })
 