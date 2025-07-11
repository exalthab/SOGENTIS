# accounts_users/web/views/profile_views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts_users.models.users_profile import UserProfile

@staff_member_required
def list_pending_profiles(request):
    profiles = UserProfile.objects.filter(status='pending')
    return render(request, 'accounts_users/profiles/pending_list.html', {'profiles': profiles})

@login_required
def profile_pending_notice(request):
    return render(request, "accounts_users/registration/profile_pending_notice.html")

