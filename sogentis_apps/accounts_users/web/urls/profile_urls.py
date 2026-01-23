# accounts_users/web/urls/profile_urls.py
from django.urls import path
from accounts_users.web.views import profile_web_views, profile

app_name = "profile"

urlpatterns = [
    path("", profile.myprofile_view, name="profile"),
    path("edit/", profile_web_views.profile_edit_view, name="profile_edit"),
    path("pending/", profile_web_views.profile_pending_notice, name="profile_pending_notice"),
    path("pending/", profile_web_views.profile_pending_notice, name="profile_refused_notice"),
]
