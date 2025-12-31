# dashboard/views/social/admin.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render


def is_social_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_social_admin)
def social_admin_home_view(request):
    return render(request, "dashboard/social/admin/home.html")
