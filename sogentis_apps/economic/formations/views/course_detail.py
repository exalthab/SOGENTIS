# economic/formations/views/course_detail.py
from django.shortcuts import render, get_object_or_404
from ..models.course import Course


def course_detail_view(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    return render(request, "formations/course_detail.html", {"course": course})
