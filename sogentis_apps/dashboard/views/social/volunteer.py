# dashboard/views/social/volunteer.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def volunteer_home_view(request):
    return render(request, "dashboard/social/volunteer/home.html")
