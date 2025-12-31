# economic/formations/views/course_list.py

from django.shortcuts import render
from django.utils.translation import get_language

from ..models.course import Course


def course_list_view(request):
    """
    Liste des formations (catalogue).
    - Filtre par recherche (q)
    """
    language = get_language()

    courses = Course.objects.all()

    q = request.GET.get("q", "").strip()

    if q:
        # Si Course est translatable (Parler) avec un champ 'title' dans translations
        try:
            courses = courses.filter(
                translations__language_code=language,
                translations__title__icontains=q,
            )
        except Exception:
            # fallback si pas de Parler ou autre champ
            courses = courses.filter(title__icontains=q)

    context = {
        "courses": courses,
        # pour que le template ne casse pas avec {% if categories %}
        "categories": [],
    }
    return render(request, "economic/formations/course_list.html", context)
