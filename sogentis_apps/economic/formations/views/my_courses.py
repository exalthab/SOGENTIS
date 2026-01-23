from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Enrollment


@login_required
def my_courses_view(request):
    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .exclude(status=Enrollment.Status.CANCELLED)
        .select_related("course", "course__category")
        .order_by("-enrolled_at")
    )
    return render(request, "economic/formations/learner/my_courses.html", {"enrollments": enrollments})
