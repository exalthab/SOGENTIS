# dashboard/views/social/member.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def member_home_view(request):
    return render(request, "dashboard/social/member/home.html")
