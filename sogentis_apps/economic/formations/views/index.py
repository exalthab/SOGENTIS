# economic/formations/views/catalog_2.py
from django.shortcuts import render
from ..models.course import Course


def formations_index_view(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, "economic/formations/index.html", {"courses": courses})
