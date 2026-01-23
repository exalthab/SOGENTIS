# economic/formations/views/learning.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _, get_language

from ..models import Course, Enrollment, Module, Lesson


@login_required
def learning_view(request, slug):
    lang = get_language()
    course = get_object_or_404(Course.objects.language(lang), slug=slug, is_active=True)

    enrollment = Enrollment.objects.filter(user=request.user, course=course).exclude(
        status=Enrollment.Status.CANCELLED
    ).first()
    if not enrollment:
        messages.warning(request, _("Vous devez être inscrit pour accéder au contenu."))
        return redirect("economic:formations:course_detail", slug=course.slug)

    modules = (
        Module.objects.language(lang)
        .filter(course=course, is_active=True)
        .prefetch_related(
            Prefetch(
                "lessons",
                queryset=Lesson.objects.language(lang).filter(is_active=True).order_by("order", "id")
            )
        )
        .order_by("order", "id")
    )

    # sélection d'une leçon (optionnel)
    lesson_id = request.GET.get("lesson")
    current_lesson = None
    if lesson_id:
        current_lesson = Lesson.objects.language(lang).filter(pk=lesson_id, module__course=course, is_active=True).first()

    return render(request, "economic/formations/learning/learning.html", {
        "course": course,
        "enrollment": enrollment,
        "modules": modules,
        "current_lesson": current_lesson,
    })




# from django.shortcuts import render, get_object_or_404
# from ..models.course import Course


# def learning_view(request, slug):
#     course = get_object_or_404(
#         Course,
#         translations__slug=slug,
#         is_active=True
#     )
#     return render(
#         request,
#         "formations/learning.html",
#         {"course": course}
#     )
