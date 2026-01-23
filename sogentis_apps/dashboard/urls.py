# dashboard/urls.py


from dashboard.urls import urlpatterns, app_name  # re-export

__all__ = ["urlpatterns", "app_name"]




# # dashboard/urls.py
# from django.urls import path, include

# app_name = "dashboard"

# urlpatterns = [
#     path(
#         "urls/",
#         include(
#             ("dashboard.urls", "urls"),
#             namespace="urls",
#         ),
#     ),
# ]







# # /dashboard/urls.py
# from django.urls import path, include

# # Imports par modules (meilleure pratique)
# from dashboard.views import (
#     profile,
#     stats,
#     orders,
#     dons,
#     donations,
#     engagements,
#     lists,
#     notes,
# )

# from dashboard.views.user.home import user_dashboard_home_view
# from dashboard.views.vendor.home import vendor_dashboard_home_view
# from dashboard.views.b2b.home import b2b_dashboard_home_view

# from dashboard.views.pending_profiles import (
#     pending_profiles_list,
#     validate_profile_view,
#     refuse_profile_view,
# )

# from dashboard.views.hub import dashboard_hub_view
# from dashboard.views.social.router import social_dashboard_router
# from dashboard.views.social.donor import (
#     donor_home_view,
#     donor_donations_list_view,
#     donor_impact_view,
#     donor_receipt_download_view,
# )
# from dashboard.views.social.member import member_home_view
# from dashboard.views.social.volunteer import volunteer_home_view
# from dashboard.views.social.institution import institution_home_view
# from dashboard.views.social.beneficiary import beneficiary_home_view
# from dashboard.views.social.admin import social_admin_home_view

# from dashboard.views.router import dashboard_router


# app_name = "dashboard"

# urlpatterns = [
#     # =====================================================
#     # ROUTER PRINCIPAL → Redirection selon rôle
#     # =====================================================
#     path("", dashboard_router, name="router"),

#     # HUB
#     path("hub/", dashboard_hub_view, name="hub"),

#     # =====================================================
#     # ESPACE ADMIN
#     # =====================================================
#     path(
#         "admin/",
#         include(
#             ("dashboard.urls.admin", "admin"),
#             namespace="admin",
#         ),
#     ),

#     # =====================================================
#     # DASHBOARDS PAR RÔLE
#     # =====================================================
#     path("user/", user_dashboard_home_view, name="home"),
#     path("vendor/", vendor_dashboard_home_view, name="vendor_home"),
#     path("b2b/", b2b_dashboard_home_view, name="b2b_home"),

#     # =====================================================
#     # PROFIL UTILISATEUR
#     # =====================================================
#     path("profile/", profile.dashboard_profile_view, name="profile"),
#     path("profile/edit/", profile.dashboard_profile_edit_view, name="profile_edit"),

#     # =====================================================
#     # STATISTIQUES
#     # =====================================================
#     path("stats/", stats.stats_view, name="stats"),

#     # =====================================================
#     # COMMANDES
#     # =====================================================
#     path("orders/", orders.orders_view, name="orders"),

#     # =====================================================
#     # ENGAGEMENTS
#     # =====================================================
#     path(
#         "engagements/",
#         engagements.dashboard_engagements_list_view,
#         name="engagements_list",
#     ),

#     # =====================================================
#     # DONS / DONATIONS
#     # =====================================================
#     path("dons/", dons.dashboard_dons_list_view, name="dons_list"),
#     path("donations/", donations.dashboard_donations_view, name="donations"),

#     # =====================================================
#     # LISTES
#     # =====================================================
#     path("lists/", lists.dashboard_lists_view, name="lists"),

#     # =====================================================
#     # NOTES
#     # =====================================================
#     path("notes/", notes.note_list_view, name="notes_list"),
#     path("notes/create/", notes.create_note_view, name="notes_create"),
#     path("notes/<int:note_id>/edit/", notes.edit_note_view, name="notes_edit"),

#     # =====================================================
#     # PROFILS EN ATTENTE
#     # =====================================================
#     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
#     path(
#         "profiles/<int:profile_id>/approve/",
#         validate_profile_view,
#         name="profile_approve",
#     ),
#     path(
#         "profiles/<int:profile_id>/refuse/",
#         refuse_profile_view,
#         name="profile_refuse",
#     ),

#     # =====================================================
#     # PÔLE SOCIAL
#     # =====================================================
#     path("social/", social_dashboard_router, name="social_router"),

#     path("social/donor/", donor_home_view, name="social_donor_home"),
#     path(
#         "social/donor/donations/",
#         donor_donations_list_view,
#         name="social_donor_donations",
#     ),
#     path(
#         "social/donor/receipt/<int:donation_id>/",
#         donor_receipt_download_view,
#         name="social_donor_receipt_download",
#     ),
#     path(
#         "social/donor/impact/",
#         donor_impact_view,
#         name="social_donor_impact",
#     ),

#     path("social/member/", member_home_view, name="social_member_home"),
#     path("social/volunteer/", volunteer_home_view, name="social_volunteer_home"),
#     path("social/institution/", institution_home_view, name="social_institution_home"),
#     path("social/beneficiary/", beneficiary_home_view, name="social_beneficiary_home"),
#     path("social/admin/", social_admin_home_view, name="social_admin_home"),
# ]







# # # /dashboard/urls.py
# # from django.urls import path, include

# # from dashboard.views import (
# #     index,
# #     profile,
# #     stats,
# #     orders,
# #     dons,
# #     donations,
# #     engagements,
# #     lists,
# #     notes,
# # )

# # from dashboard.views.user.home import user_dashboard_home_view
# # from dashboard.views.vendor.home import vendor_dashboard_home_view
# # from dashboard.views.b2b.home import b2b_dashboard_home_view

# # from dashboard.views.pending_profiles import (
# #     pending_profiles_list,
# #     validate_profile_view,
# #     refuse_profile_view,
# # )

# # from dashboard.views.hub import dashboard_hub_view
# # from dashboard.views.social.router import social_dashboard_router
# # from dashboard.views.social.donor import (
# #     donor_donations_list_view,
# #     donor_impact_view,
# #     donor_receipt_download_view,
# #     donor_home_view,
# # )
# # from dashboard.views.social.member import member_home_view
# # from dashboard.views.social.volunteer import volunteer_home_view
# # from dashboard.views.social.institution import institution_home_view
# # from dashboard.views.social.beneficiary import beneficiary_home_view
# # from dashboard.views.social.admin import social_admin_home_view

# # from dashboard.views.router import dashboard_router


# app_name = "dashboard"

# urlpatterns = [
#     # =====================================================
#     # ROUTER PRINCIPAL → Redirection selon rôle
#     # =====================================================
#     path("", dashboard_router, name="router"),

#     # HUB (page centrale éventuelle)
#     path("hub/", dashboard_hub_view, name="hub"),

#     # =====================================================
#     # ESPACE ADMIN  (sous-namespace dashboard:admin:xxx)
#     # =====================================================
#     path(
#         "admin/",
#         include(
#             ("dashboard.urls.admin", "admin"),
#             namespace="admin",
#         ),
#     ),

#     # =====================================================
#     # DASHBOARDS PAR RÔLE
#     # =====================================================
#     # Dashboard utilisateur (standard)
#     path("user/", user_dashboard_home_view, name="home"),

#     # Dashboard vendeur
#     path("vendor/", vendor_dashboard_home_view, name="vendor_home"),

#     # Dashboard B2B
#     path("b2b/", b2b_dashboard_home_view, name="b2b_home"),

#     # =====================================================
#     # PROFIL UTILISATEUR (dans le dashboard)
#     # =====================================================
#     path("profile/", profile.dashboard_profile_view, name="profile"),
#     path("profile/edit/", profile.dashboard_profile_edit_view, name="profile_edit"),

#     # =====================================================
#     # STATISTIQUES
#     # =====================================================
#     path("stats/", stats.stats_view, name="stats"),

#     # =====================================================
#     # COMMANDES
#     # =====================================================
#     path("orders/", orders.orders_view, name="orders"),

#     # =====================================================
#     # ENGAGEMENTS
#     # =====================================================
#     path(
#         "engagements/",
#         engagements.dashboard_engagements_list_view,
#         name="engagements_list",
#     ),

#     # =====================================================
#     # DONS / DONATIONS
#     # =====================================================
#     path("dons/", dons.dashboard_dons_list_view, name="dons_list"),
#     path("donations/", donations.dashboard_donations_view, name="donations"),

#     # =====================================================
#     # LISTES DIVERSES
#     # =====================================================
#     path("lists/", lists.dashboard_lists_view, name="lists"),

#     # =====================================================
#     # NOTES
#     # =====================================================
#     path("notes/", notes.note_list_view, name="notes_list"),
#     path("notes/create/", notes.create_note_view, name="notes_create"),
#     path("notes/<int:note_id>/edit/", notes.edit_note_view, name="notes_edit"),

#     # =====================================================
#     # PROFILS EN ATTENTE (Admin Dashboard)
#     # =====================================================
#     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
#     path(
#         "profiles/<int:profile_id>/approve/",
#         validate_profile_view,
#         name="profile_approve",
#     ),
#     path(
#         "profiles/<int:profile_id>/refuse/",
#         refuse_profile_view,
#         name="profile_refuse",
#     ),

#     # =====================================================
#     # PÔLE SOCIAL — DASHBOARDS SPÉCIFIQUES
#     # =====================================================
#     path("social/", social_dashboard_router, name="social_router"),

#     path("social/donor/", donor_home_view, name="social_donor_home"),
#     path(
#         "social/donor/donations/",
#         donor_donations_list_view,
#         name="social_donor_donations",
#     ),
#     path(
#         "social/donor/receipt/<int:donation_id>/",
#         donor_receipt_download_view,
#         name="social_donor_receipt_download",
#     ),
#     path(
#         "social/donor/impact/",
#         donor_impact_view,
#         name="social_donor_impact",
#     ),

#     path("social/member/", member_home_view, name="social_member_home"),
#     path("social/volunteer/", volunteer_home_view, name="social_volunteer_home"),
#     path("social/institution/", institution_home_view, name="social_institution_home"),
#     path("social/beneficiary/", beneficiary_home_view, name="social_beneficiary_home"),
#     path("social/admin/", social_admin_home_view, name="social_admin_home"),
# ]









# # # /dashboard/urls.py
# # from django.urls import path, include

# # from dashboard.views import index, profile, stats, orders, dons, donations, engagements, lists, notes
# # from dashboard.views.user.home import user_dashboard_home_view, user_dashboard_view
# # from dashboard.views.vendor.home import vendor_dashboard_home_view, vendor_index_view
# # from dashboard.views.b2b.home import b2b_dashboard_home_view, b2b_dashboard_view

# # from dashboard.views.pending_profiles import (
# #     pending_profiles_list,
# #     validate_profile_view,
# #     refuse_profile_view,
# # )

# # from dashboard.views.hub import dashboard_hub_view
# # from dashboard.views.social.router import social_dashboard_router
# # from dashboard.views.social.donor import donor_donations_list_view, donor_impact_view
# # from dashboard.views.social.donor import donor_receipt_download_view


# # from dashboard.views.social.donor import donor_home_view
# # from dashboard.views.social.member import member_home_view
# # from dashboard.views.social.volunteer import volunteer_home_view
# # from dashboard.views.social.institution import institution_home_view
# # from dashboard.views.social.beneficiary import beneficiary_home_view
# # from dashboard.views.social.admin import social_admin_home_view
# # from dashboard.views.router import dashboard_router
# # from dashboard.views.router import dashboard_router



# # app_name = "dashboard"

# # urlpatterns = [
# #     # =====================================================
# #     # ROUTER → Redirection selon rôle
# #     # =====================================================
# #     path("", dashboard_router, name="router"),
# #     path("", include("dashboard.urls.admin")),
# #     path("", vendor_dashboard_home_view, name="index"),

# #     # HUB
# #     path("", dashboard_hub_view, name="hub"),

# #     # =====================================================
# #     # DASHBOARDS PAR RÔLE
# #     # =====================================================
# #     path("user/", user_dashboard_home_view, name="home"),    
# #     path("vendor/", vendor_dashboard_home_view, name="index"),
# #     path("b2b/", b2b_dashboard_home_view, name="b2b_home"),

# #     # =====================================================
# #     # PROFIL UTILISATEUR
# #     # =====================================================
# #     path("profile/", profile.dashboard_profile_view, name="profile"),
# #     path("profile/edit/", profile.dashboard_profile_edit_view, name="profile_edit"),

# #     # =====================================================
# #     # STATISTIQUES
# #     # =====================================================
# #     path("stats/", stats.stats_view, name="stats"),

# #     # =====================================================
# #     # COMMANDES
# #     # =====================================================
# #     path("orders/", orders.orders_view, name="orders"),

# #     # =====================================================
# #     # ENGAGEMENTS
# #     # =====================================================
# #     path("engagements/", engagements.dashboard_engagements_list_view, name="engagements_list"),

# #     # =====================================================
# #     # DONS / DONATIONS
# #     # =====================================================
# #     path("dons/", dons.dashboard_dons_list_view, name="dons_list"),
# #     path("donations/", donations.dashboard_donations_view, name="donations"),

# #     # =====================================================
# #     # LISTES DIVERSES
# #     # =====================================================
# #     path("lists/", lists.dashboard_lists_view, name="lists"),

# #     # =====================================================
# #     # NOTES
# #     # =====================================================
# #     path("notes/", notes.note_list_view, name="notes_list"),
# #     path("notes/create/", notes.create_note_view, name="notes_create"),
# #     path("notes/<int:note_id>/edit/", notes.edit_note_view, name="notes_edit"),

# #     # =====================================================
# #     # PROFILS EN ATTENTE (Admin Dashboard)
# #     # =====================================================
# #     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
# #     path("profiles/<int:profile_id>/approve/", validate_profile_view, name="profile_approve"),
# #     path("profiles/<int:profile_id>/refuse/", refuse_profile_view, name="profile_refuse"),
    
# #     # SOCIAL
# #     path("social/", social_dashboard_router, name="social_router"),

# #     path("social/donor/", donor_home_view, name="social_donor_home"),
# #     path(
# #         "social/donor/donations/",
# #         donor_donations_list_view,
# #         name="social_donor_donations"
# #     ),  
# #     path(
# #         "social/donor/receipt/<int:donation_id>/",
# #         donor_receipt_download_view,
# #         name="social_donor_receipt_download",
# #     ),
# #     path(
# #     "social/donor/impact/",
# #     donor_impact_view,
# #     name="social_donor_impact",
# #     ),
# #     path("social/member/", member_home_view, name="social_member_home"),
# #     path("social/volunteer/", volunteer_home_view, name="social_volunteer_home"),
# #     path("social/institution/", institution_home_view, name="social_institution_home"),
# #     path("social/beneficiary/", beneficiary_home_view, name="social_beneficiary_home"),
# #     path("social/admin/", social_admin_home_view, name="social_admin_home"),


# # ]











# # # dashboard/urls.py

# # from django.urls import path

# # from dashboard.views import index, profile, stats, orders, dons, donations, engagements, lists, notes
# # from dashboard.views.router import dashboard_router
# # from dashboard.views.user.home import user_dashboard_view
# # from dashboard.views.vendor.index import vendor_dashboard_view
# # from dashboard.views.b2b.home import b2b_dashboard_view
# # from dashboard.views.pending_profiles import (
# #     pending_profiles_list,
# #     validate_profile_view,
# #     refuse_profile_view,
# # )

# # app_name = "dashboard"

# # urlpatterns = [
# #     # Dashboard
# #     path("", dashboard_router, name="router"),
# #     # Dashboards par rôle
# #     path("user/", user_dashboard_view, name="user_index"),    
# #     path("vendor/", vendor_dashboard_view, name="vendor_home"),
# #     path("b2b/", b2b_dashboard_view, name="b2b_home"),
    
# #     # path("", index.index_view, name="index"),
# #     # path("home/", index.index_redirect_view, name="home_redirect"),


# #     # Profil utilisateur
# #     path("profile/", profile.dashboard_profile_view, name="profile"),
# #     path("profile/edit/", profile.dashboard_profile_edit_view, name="profile_edit"),

# #     # Stats
# #     path("stats/", stats.stats_view, name="stats"),
    
# #     # Orders
# #     path("orders/", orders.orders_view, name="orders"),

# #     # Engagements
# #     path("engagements/", engagements.dashboard_engagements_list_view, name="engagements_list"),

# #     # Dons
# #     path("dons/", dons.dashboard_dons_list_view, name="dons_list"),

# #     # path("donations/", donations.donations_view, name="donations"),
# #     path("donations/", donations.dashboard_donations_view, name="donations"),

# #     # Listes diverses
# #     path("lists/", lists.dashboard_lists_view, name="lists"),

# #     # # Notes
# #     # path("notes/", notes.note_list_view, name="notes_list"),
# #     # path("notes/create/", notes.create_note_view, name="create_note"),
# #     # path("notes/<int:pk>/edit/", notes.edit_note_view, name="edit_note"),

# #     # Notes
# #     path("notes/", notes.note_list_view, name="notes"),
# #     path("notes/create/", notes.create_note_view, name="notes_create"),
# #     path("notes/<int:note_id>/edit/", notes.edit_note_view, name="notes_edit"),

# #     # ⚠️ PROFILS EN ATTENTE (Admin Dashboard)
# #     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
# #     path("profiles/<int:profile_id>/approve/", validate_profile_view, name="profile_approve"),
# #     path("profiles/<int:profile_id>/refuse/", refuse_profile_view, name="profile_refuse"),
# # ]




# # urlpatterns = [
# #     # 🏠 Accueil du dashboard
# #     path("", views.dashboard_index_view, name="index"),

# #     # 👤 Profil utilisateur
# #     path("profile/", views.dashboard_profile_view, name="profile"),

# #     # 📊 Statistiques
# #     path("stats/", views.dashboard_stats_view, name="stats"),

# #     # 📋 Historique des engagements
# #     path("engagements/", views.engagements_list_view, name="engagements_list"),

# #     # 💝 Historique des dons
# #     path("dons/", views.dons_list_view, name="dons_list"),
# # ]


# # urlpatterns = [
#     # path("", index.dashboard_index_view, name="index"),
#     # path("profile/", profile.dashboard_profile_view, name="profile"),
#     # path("stats/", stats.dashboard_stats_view, name="stats"),
#     # path("dons/", dons.dons_list_view, name="dons"),
#     # path("engagements/", engagements.engagements_list_view, name="engagements"),
#     # path("lists/", lists.dashboard_lists_view, name="lists"),
# # ]
