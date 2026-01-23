# economic/formations/views/course_detail.py
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language

from ..models import Course, Enrollment


def course_detail_view(request, slug):
    lang = get_language()
    course = get_object_or_404(Course.objects.language(lang), slug=slug, is_active=True)

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exclude(
            status=Enrollment.Status.CANCELLED
        ).exists()

    return render(request, "economic/formations/courses/course_detail.html", {
        "course": course,
        "is_enrolled": is_enrolled,
        "upcoming_sessions": course.sessions.filter(is_cancelled=False).order_by("starts_at")[:12],
    })






# from django.shortcuts import render, get_object_or_404
# from ..models.course import Course


# def course_detail_view(request, pk):
#     course = get_object_or_404(Course, pk=pk, is_active=True)
#     return render(request, "formations/course_detail.html", {"course": course})
