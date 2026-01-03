# dashboard/views/social/admin.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from dashboard.views.utils import breadcrumb

@staff_member_required
def social_admin_home_view(request):
    return render(request, "dashboard/social/admin/home.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Social"), "/dashboard/social/"), (_("Admin social"), None)),
    })




# # dashboard/views/social/admin.py
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render


# def is_social_admin(user):
#     return user.is_staff


# @login_required
# @user_passes_test(is_social_admin)
# def social_admin_home_view(request):
#     return render(request, "dashboard/social/admin/home.html")
