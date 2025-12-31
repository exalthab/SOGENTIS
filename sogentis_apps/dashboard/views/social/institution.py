# dashboard/views/social/institution.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def institution_home_view(request):
    return render(request, "dashboard/social/institution/home.html")
