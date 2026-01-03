# dashboard/urls/b2b.py
from django.urls import path
from dashboard.views.b2b.home import b2b_dashboard_home_view

app_name = "dashboard_b2b"

urlpatterns = [
    path("", b2b_dashboard_home_view, name="home"),
]





# # dashboard/urls/b2b.py 01/01/2026
# from django.urls import path

# from dashboard.views.b2b.home import b2b_dashboard_home_view
# from dashboard.views.b2b.users import (
#     b2b_users_list_view,
#     b2b_user_create_view,
#     b2b_user_update_view,
# )

# app_name = "dashboard_b2b"

# urlpatterns = [
#     # Dashboard B2B
#     path("", b2b_dashboard_home_view, name="home"),

#     # Gestion utilisateurs B2B
#     path("users/", b2b_users_list_view, name="users"),
#     path("users/add/", b2b_user_create_view, name="user_add"),
#     path("users/<int:pk>/edit/", b2b_user_update_view, name="user_edit"),
# ]



# # dashboard/urls/b2b.py
# from django.urls import path
# from dashboard.views.b2b.home import b2b_dashboard_view

# app_name = "b2b"

# urlpatterns = [
#     path("", b2b_dashboard_view, name="home"),
# ]
