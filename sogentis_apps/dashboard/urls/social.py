from django.urls import path

from dashboard.views.social.router import social_dashboard_router

from dashboard.views.social.donor import (
    donor_home_view,
    donor_donations_list_view,
    donor_impact_view,
    donor_receipt_download_view,
)
from dashboard.views.social.member import member_home_view
from dashboard.views.social.volunteer import volunteer_home_view
from dashboard.views.social.institution import institution_home_view
from dashboard.views.social.beneficiary import beneficiary_home_view
from dashboard.views.social.admin import social_admin_home_view

app_name = "dashboard_social"

urlpatterns = [
    # Router social (redirige selon rôle social)
    path("", social_dashboard_router, name="router"),

    # Donor
    path("donor/", donor_home_view, name="donor_home"),
    path("donor/donations/", donor_donations_list_view, name="donor_donations"),
    path("donor/receipt/<int:donation_id>/", donor_receipt_download_view, name="donor_receipt_download"),
    path("donor/impact/", donor_impact_view, name="donor_impact"),

    # Member / Volunteer / Institution / Beneficiary / Admin
    path("member/", member_home_view, name="member_home"),
    path("volunteer/", volunteer_home_view, name="volunteer_home"),
    path("institution/", institution_home_view, name="institution_home"),
    path("beneficiary/", beneficiary_home_view, name="beneficiary_home"),
    path("admin/", social_admin_home_view, name="admin_home"),
]






# # dashboard/urls/social.py

# from django.urls import path
# from dashboard.views.social.home import social_dashboard_home_view

# app_name = "dashboard_social"

# urlpatterns = [
#     path("", social_dashboard_home_view, name="home"),
# ]
