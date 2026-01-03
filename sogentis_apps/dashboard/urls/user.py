# dashboard/urls/user.py
from django.urls import path
from dashboard.views.user.home import user_dashboard_home_view
from dashboard.views.orders import orders_view

app_name = "dashboard_user"

urlpatterns = [
    path("", user_dashboard_home_view, name="home"),
    path("orders/", orders_view, name="orders"),
]





# # dashboard/urls/user.py 01/01/2026
# from django.urls import path
# from dashboard.views.user.home import user_dashboard_home_view

# app_name = "dashboard_user"

# urlpatterns = [
#     path("", user_dashboard_home_view, name="home"),
# ]
