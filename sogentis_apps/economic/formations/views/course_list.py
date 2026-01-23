# economic/formations/views/course_list.py
from __future__ import annotations

from django.shortcuts import render
from django.utils.translation import get_language

from ..models import Course, CourseCategory


def course_list_view(request):
    lang = get_language() or "fr"

    courses = (
        Course.objects.filter(is_active=True)
        .filter(translations__language_code=lang)
        .select_related("category")
        .order_by("-published_at", "-created_at")
        .distinct()
    )

    categories = (
        CourseCategory.objects.filter(is_active=True)
        .filter(translations__language_code=lang)
        .order_by("order", "id")
        .distinct()
    )

    q = (request.GET.get("q") or "").strip()
    category_slug = (request.GET.get("category") or "").strip()
    ctype = (request.GET.get("type") or "").strip()

    if q:
        courses = courses.filter(translations__title__icontains=q).distinct()

    if category_slug:
        # slug non traduit en général → OK direct
        courses = courses.filter(category__slug=category_slug)

    if ctype in {"online", "onsite", "blended"}:
        courses = courses.filter(type=ctype)

    return render(
        request,
        "economic/formations/courses/course_list.html",
        {
            "courses": courses,
            "categories": categories,
            "q": q,
            "category_selected": category_slug,
            "type_selected": ctype,
        },
    )



# # economic/formations/views/course_list.py
# from __future__ import annotations

# from django.shortcuts import render
# from django.utils.translation import get_language

# from ..models import Course, CourseCategory


# def _lang_code() -> str:
#     lang = (get_language() or "fr").strip()
#     # ex: "fr-fr" -> "fr"
#     return lang.split("-")[0]


# def _parler_lang_filter(qs, lang: str):
#     """
#     Filtre robuste par langue Parler sans dépendre de `.language()`.
#     """
#     return qs.filter(translations__language_code=lang).distinct()


# def course_list_view(request):
#     lang = _lang_code()

#     # Base querysets
#     courses = (
#         Course.objects.filter(is_active=True)
#         .select_related("category")
#         .order_by("-published_at", "-created_at")
#     )
#     categories = CourseCategory.objects.filter(is_active=True).order_by("order", "id")

#     # Lang filter (parler)
#     courses = _parler_lang_filter(courses, lang)
#     categories = _parler_lang_filter(categories, lang)

#     # Filters (GET)
#     q = (request.GET.get("q") or "").strip()
#     category_slug = (request.GET.get("category") or "").strip()
#     ctype = (request.GET.get("type") or "").strip()

#     if q:
#         # Recherche sur les champs traduits
#         courses = courses.filter(
#             translations__title__icontains=q
#         )

#     if category_slug:
#         courses = courses.filter(category__slug=category_slug)

#     if ctype in {"online", "onsite", "blended"}:
#         courses = courses.filter(type=ctype)

#     return render(
#         request,
#         "economic/formations/courses/course_list.html",
#         {
#             "lang": lang,
#             "courses": courses,
#             "categories": categories,
#             "q": q,
#             "category_selected": category_slug,
#             "type_selected": ctype,
#         },
#     )





# # economic/formations/views/course_list.py
# from django.shortcuts import render
# from django.utils.translation import get_language

# from ..models import Course, CourseCategory


# def course_list_view(request):
#     lang = get_language()

#     courses = Course.objects.filter(is_active=True).language(lang).select_related("category").order_by("-published_at", "-created_at")
#     categories = CourseCategory.objects.filter(is_active=True).language(lang).order_by("order", "id")

#     q = (request.GET.get("q") or "").strip()
#     category_slug = (request.GET.get("category") or "").strip()
#     ctype = (request.GET.get("type") or "").strip()

#     if q:
#         courses = courses.filter(translations__language_code=lang, translations__title__icontains=q)

#     if category_slug:
#         courses = courses.filter(category__slug=category_slug)

#     if ctype in {"online", "onsite", "blended"}:
#         courses = courses.filter(type=ctype)

#     return render(request, "economic/formations/courses/course_list.html", {
#         "courses": courses,
#         "categories": categories,
#         "q": q,
#         "category_selected": category_slug,
#         "type_selected": ctype,
#     })







# from django.shortcuts import render
# from django.utils.translation import get_language

# from ..models.course import Course


# def course_list_view(request):
#     """
#     Liste des formations (catalogue).
#     - Filtre par recherche (q)
#     """
#     language = get_language()

#     courses = Course.objects.all()

#     q = request.GET.get("q", "").strip()

#     if q:
#         # Si Course est translatable (Parler) avec un champ 'title' dans translations
#         try:
#             courses = courses.filter(
#                 translations__language_code=language,
#                 translations__title__icontains=q,
#             )
#         except Exception:
#             # fallback si pas de Parler ou autre champ
#             courses = courses.filter(title__icontains=q)

#     context = {
#         "courses": courses,
#         # pour que le template ne casse pas avec {% if categories %}
#         "categories": [],
#     }
#     return render(request, "economic/formations/course_list.html", context)
