# economic/formations/views/learning.py
from django.shortcuts import render, get_object_or_404
from ..models.course import Course


def learning_view(request, slug):
    course = get_object_or_404(
        Course,
        translations__slug=slug,
        is_active=True
    )
    return render(
        request,
        "formations/learning.html",
        {"course": course}
    )
