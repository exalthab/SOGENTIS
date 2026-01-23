# dashboard/urls/admin.py
from django.urls import path

from dashboard.views.admin.home import admin_home_view
from dashboard.views.admin.moderation import (
    admin_moderation_view,
    admin_application_approve_view,
    admin_application_reject_view,
)
from dashboard.views.admin.reports import admin_reports_view
from dashboard.views.admin.settings import admin_settings_view
from dashboard.views.admin.users import admin_users_list_view

app_name = "dashboard_admin"

urlpatterns = [
    path("", admin_home_view, name="index"),
    path("moderation/", admin_moderation_view, name="moderation"),

    # ✅ Actions moderation (POST)
    path("moderation/applications/<int:pk>/approve/", admin_application_approve_view, name="application_approve"),
    path("moderation/applications/<int:pk>/reject/", admin_application_reject_view, name="application_reject"),

    path("reports/", admin_reports_view, name="reports"),
    path("settings/", admin_settings_view, name="settings"),
    path("users/", admin_users_list_view, name="users"),
]





# # dashboard/urls/admin.py
# from django.urls import path

# from dashboard.views.admin.home import admin_home_view
# from dashboard.views.admin.moderation import admin_moderation_view
# from dashboard.views.admin.reports import admin_reports_view
# from dashboard.views.admin.settings import admin_settings_view
# from dashboard.views.admin.users import admin_users_list_view

# app_name = "dashboard_admin"

# urlpatterns = [
#     path("", admin_home_view, name="index"),
#     path("moderation/", admin_moderation_view, name="moderation"),
#     path("reports/", admin_reports_view, name="reports"),
#     path("settings/", admin_settings_view, name="settings"),
#     path("users/", admin_users_list_view, name="users"),
# ]






# # dashboard/urls/admin.py
# from django.urls import path
# from dashboard.views.admin.home import admin_home_view

# app_name = "dashboard_admin"

# urlpatterns = [
#     path("", admin_home_view, name="index"),
# ]







# # dashboard/views/urls/admin.py
# from django.urls import path

# from dashboard.views.admin.home import admin_home_view
# # from dashboard.views.admin.users import admin_users_list_view
# # from dashboard.views.admin.moderation import admin_moderation_view
# # from dashboard.views.admin.reports import admin_reports_view
# # from dashboard.views.admin.settings import admin_settings_view

# app_name = "dashboard_admin"

# urlpatterns = [
#     path("", admin_home_view, name="index"),
#     # path("users/", admin_users_list_view, name="users"),
#     # path("moderation/", admin_moderation_view, name="moderation"),
#     # path("reports/", admin_reports_view, name="reports"),
#     # path("settings/", admin_settings_view, name="settings"),
# ]







# # /dashboard/urls/admin.py
# from django.urls import path
# from dashboard.views.admin.moderation import moderation_dashboard
# from dashboard.views.admin.reports import reports_dashboard
# from dashboard.views.admin.settings import admin_settings
# from dashboard.views.admin.users import users_list
# from django.urls import path
# from dashboard.views.admin.home import (
#     admin_dashboard_home_view,
#     staff_dashboard_home_view,
# )

# app_name = "dashboard_admin"

# urlpatterns = [
#     # Admin
#     path("", admin_dashboard_home_view, name="home"),
#     # Staff
#     path("staff/", staff_dashboard_home_view, name="staff"),
#     path("moderation/", moderation_dashboard, name="moderation"),
#     path("reports/", reports_dashboard, name="reports"),
#     path("settings/", admin_settings, name="settings"),
#     path("users/", users_list, name="users"),
# ]

