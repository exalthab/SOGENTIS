# dashboard/views/social/beneficiary.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def beneficiary_home_view(request):
    return render(request, "dashboard/social/beneficiary/home.html")
