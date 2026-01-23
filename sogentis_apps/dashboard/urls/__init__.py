# dashboard/urls/__init__.py
from django.urls import path, include

from dashboard.views.router import dashboard_router
from dashboard.views.dashboard_hub import hub_view
from dashboard.views.account_pending import account_pending_view

from dashboard.views import (
    stats,
    orders,
    dons,
    donations,
    engagements,
    lists,
    notes,
)

from dashboard.views.dashboard_profile import (
    dashboard_profile_view,
    dashboard_profile_edit_view,
)

from dashboard.views.pending_profiles import (
    pending_profiles_list,
    validate_profile_view,
    refuse_profile_view,
)

app_name = "dashboard"

urlpatterns = [
    path("", dashboard_router, name="router"),
    path("hub/", hub_view, name="hub"),
    path("account/pending/", account_pending_view, name="account_pending"),

    path("admin/", include(("dashboard.urls.admin", "dashboard_admin"), namespace="admin")),

    path("user/", include(("dashboard.urls.user", "dashboard_user"), namespace="user")),
    path("vendor/", include(("dashboard.urls.vendor", "dashboard_vendor"), namespace="vendor")),
    path("b2b/", include(("dashboard.urls.b2b", "dashboard_b2b"), namespace="b2b")),

    # ✅ FIX ICI
    path("formations/", include(("dashboard.urls.formations", "dashboard_formations"), namespace="formations")),

    path("social/", include(("dashboard.urls.social", "dashboard_social"), namespace="social")),

    path("profile/", dashboard_profile_view, name="profile"),
    path("profile/edit/", dashboard_profile_edit_view, name="profile_edit"),

    path("stats/", stats.stats_view, name="stats"),
    path("orders/", orders.orders_view, name="orders"),
    path("lists/", lists.dashboard_lists_view, name="lists"),

    path("engagements/", engagements.dashboard_engagements_list_view, name="engagements_list"),

    path("dons/", dons.dashboard_dons_list_view, name="dons_list"),
    path("donations/", donations.dashboard_dons_list_view, name="donations"),

    path("notes/", notes.note_list_view, name="notes_list"),
    path("notes/create/", notes.create_note_view, name="note_create"),
    path("notes/<int:pk>/edit/", notes.edit_note_view, name="note_edit"),

    path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
    # path("profiles/<int:profile_id>/approve/", validate_profile_view, name="profile_approve"),
    # path("profiles/<int:profile_id>/refuse/", refuse_profile_view, name="profile_refuse"),
    path("profiles/<int:user_id>/approve/", validate_profile_view, name="profile_approve"),
    path("profiles/<int:user_id>/refuse/", refuse_profile_view, name="profile_refuse"),

]





# # dashboard/urls/__init__.py
# from django.urls import path, include

# from dashboard.views.router import dashboard_router
# from dashboard.views.dashboard_hub import hub_view

# from dashboard.views import (
#     stats,
#     orders,
#     dons,
#     donations,
#     engagements,
#     lists,
#     notes,
# )

# from dashboard.views.dashboard_profile import (
#     dashboard_profile_view,
#     dashboard_profile_edit_view,
# )

# from dashboard.views.pending_profiles import (
#     pending_profiles_list,
#     validate_profile_view,
#     refuse_profile_view,
# )
 
# app_name = "urls"

# urlpatterns = [
#     # =====================================================
#     # ROUTER PRINCIPAL → redirection selon rôle
#     # =====================================================
#     path("", dashboard_router, name="router"),

#     # HUB (utilisé par login redirect => dashboard:hub)
#     path("hub/", hub_view, name="hub"),

#     # =====================================================
#     # ESPACE ADMIN (dashboard interne)
#     # Namespace: dashboard:admin:*
#     # =====================================================
#     path(
#         "admin/",
#         include(("dashboard.urls.admin", "dashboard_admin"), namespace="admin"),
#     ),

#     # =====================================================
#     # ESPACES PAR RÔLE
#     # Namespaces: dashboard:user:* / dashboard:vendor:* / dashboard:b2b:*
#     # =====================================================
#     path(
#         "user/",
#         include(("dashboard.urls.user", "dashboard_user"), namespace="user"),
#     ),
#     path(
#         "vendor/",
#         include(("dashboard.urls.vendor", "dashboard_vendor"), namespace="vendor"),
#     ),
#     path(
#         "b2b/",
#         include(("dashboard.urls.b2b", "dashboard_b2b"), namespace="b2b"),
#     ),
#     path(
#         "formations/",
#         include(("dashboard.urls.b2b", "dashboard_formations"), namespace="formations"),
#     ),

#     # =====================================================
#     # MODULE SOCIAL (router + sous-routes)
#     # Namespace: dashboard:social:*
#     # =====================================================
#     path(
#         "social/",
#         include(("dashboard.urls.social", "dashboard_social"), namespace="social"),
#     ),

#     # =====================================================
#     # PROFILÉFÉRENCE PROFIL
#     # =====================================================
#     path("profile/", dashboard_profile_view, name="profile"),
#     path("profile/edit/", dashboard_profile_edit_view, name="profile_edit"),

#     # =====================================================
#     # STATS / ORDERS / LISTES
#     # =====================================================
#     path("stats/", stats.stats_view, name="stats"),
#     path("orders/", orders.orders_view, name="orders"),
#     path("lists/", lists.dashboard_lists_view, name="lists"),

#     # =====================================================
#     # ENGAGEMENTS
#     # =====================================================
#     path("engagements/", engagements.dashboard_engagements_list_view, name="engagements_list"),

#     # =====================================================
#     # DONS / DONATIONS
#     # =====================================================
#     path("dons/", dons.dashboard_dons_list_view, name="dons_list"),
#     path("donations/", donations.dashboard_dons_list_view, name="donations"),

#     # =====================================================
#     # NOTES
#     # =====================================================
#     path("notes/", notes.note_list_view, name="notes_list"),
#     path("notes/create/", notes.create_note_view, name="note_create"),
#     path("notes/<int:pk>/edit/", notes.edit_note_view, name="note_edit"),

#     # =====================================================
#     # PROFILS EN ATTENTE (validation)
#     # =====================================================
#     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
#     path("profiles/<int:profile_id>/approve/", validate_profile_view, name="profile_approve"),
#     path("profiles/<int:profile_id>/refuse/", refuse_profile_view, name="profile_refuse"),
# ]






# # dashboard/views/urls/__init__.py
# from django.urls import path, include

# from dashboard.views.router import dashboard_router
# from dashboard.views.dashboard_hub import hub_view

# from dashboard.views import (
#     dashboard_profile,
#     stats,
#     orders,
#     dons,
#     donations,
#     engagements,
#     lists,
#     notes,
# )

# from dashboard.views.pending_profiles import (
#     pending_profiles_list,
#     validate_profile_view,
#     refuse_profile_view,
# )

# app_name = "dashboard"

# urlpatterns = [
#     # =====================================================
#     # ROUTER PRINCIPAL → redirection selon rôle
#     # =====================================================
#     path("", dashboard_router, name="router"),

#     # HUB (optionnel)
#     path("hub/", hub_view, name="hub"),

#     # =====================================================
#     # ESPACE ADMIN (dashboard interne)
#     # Namespace: dashboard:admin:*
#     # =====================================================
#     path(
#         "admin/",
#         include(("dashboard.urls.admin", "dashboard_admin"), namespace="admin"),
#     ),

#     # =====================================================
#     # ESPACES PAR RÔLE
#     # Namespaces: dashboard:user:* / dashboard:vendor:* / dashboard:b2b:*
#     # =====================================================
#     path(
#         "user/",
#         include(("dashboard.urls.user", "dashboard_user"), namespace="user"),
#     ),
#     path(
#         "vendor/",
#         include(("dashboard.urls.vendor", "dashboard_vendor"), namespace="vendor"),
#     ),
#     path(
#         "b2b/",
#         include(("dashboard.urls.b2b", "dashboard_b2b"), namespace="b2b"),
#     ),

#     # =====================================================
#     # MODULE SOCIAL (router + sous-routes)
#     # Namespace: dashboard:social:*
#     # =====================================================
#     path(
#         "social/",
#         include(("dashboard.urls.social", "dashboard_social"), namespace="social"),
#     ),

#     # =====================================================
#     # PROFIL UTILISATEUR
#     # =====================================================
#     path("profile/", dashboard_profile.dashboard_profile_view, name="profile"),
#     path("profile/edit/", dashboard_profile.dashboard_profile_edit_view, name="profile_edit"),

#     # =====================================================
#     # STATS / ORDERS / LISTES
#     # =====================================================
#     path("stats/", stats.stats_view, name="stats"),
#     path("orders/", orders.orders_view, name="orders"),
#     path("lists/", lists.dashboard_lists_view, name="lists"),

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
#     path("donations/", donations.dashboard_dons_list_view, name="donations"),

#     # =====================================================
#     # NOTES (STANDARD)
#     # =====================================================
#     path("notes/", notes.note_list_view, name="notes_list"),
#     path("notes/create/", notes.create_note_view, name="note_create"),
#     path("notes/<int:pk>/edit/", notes.edit_note_view, name="note_edit"),

#     # =====================================================
#     # PROFILS EN ATTENTE (validation)
#     # =====================================================
#     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
#     path("profiles/<int:profile_id>/approve/", validate_profile_view, name="profile_approve"),
#     path("profiles/<int:profile_id>/refuse/", refuse_profile_view, name="profile_refuse"),
# ]





# # dashboard/urls/__init__.py
# from django.urls import path, include

# from dashboard.views.router import dashboard_router
# from dashboard.views.hub import dashboard_hub_view

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

# from dashboard.views.pending_profiles import (
#     pending_profiles_list,
#     validate_profile_view,
#     refuse_profile_view,
# )

# app_name = "dashboard"

# urlpatterns = [
#     # =====================================================
#     # ROUTER PRINCIPAL → redirection selon rôle
#     # =====================================================
#     path("", dashboard_router, name="router"),

#     # HUB (optionnel)
#     path("hub/", dashboard_hub_view, name="hub"),

#     # =====================================================
#     # ESPACE ADMIN (dashboard interne)
#     # =====================================================
#     path(
#         "admin/",
#         include(("dashboard.urls.admin", "dashboard_admin"), namespace="admin"),
#     ),

#     # =====================================================
#     # ESPACES PAR RÔLE
#     # =====================================================
#     path(
#         "user/",
#         include(("dashboard.urls.user", "dashboard_user"), namespace="user"),
#     ),
#     path(
#         "vendor/",
#         include(("dashboard.urls.vendor", "dashboard_vendor"), namespace="vendor"),
#     ),
#     path(
#         "b2b/",
#         include(("dashboard.urls.b2b", "dashboard_b2b"), namespace="b2b"),
#     ),

#     # =====================================================
#     # MODULE SOCIAL (router + sous-routes)
#     # =====================================================
#     path(
#         "social/",
#         include(("dashboard.urls.social", "dashboard_social"), namespace="social"),
#     ),

#     # =====================================================
#     # PROFIL UTILISATEUR
#     # =====================================================
#     path("profile/", profile.dashboard_profile_view, name="profile"),
#     path("profile/edit/", profile.dashboard_profile_edit_view, name="profile_edit"),

#     # =====================================================
#     # STATS / ORDERS / LISTES
#     # =====================================================
#     path("stats/", stats.stats_view, name="stats"),
#     path("orders/", orders.orders_view, name="orders"),
#     path("lists/", lists.dashboard_lists_view, name="lists"),

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
#     # NOTES
#     # =====================================================
#     path("notes/", notes.note_list_view, name="notes_list"),
#     path("notes/create/", notes.create_note_view, name="notes_create"),
#     path("notes/<int:note_id>/edit/", notes.edit_note_view, name="notes_edit"),

#     # =====================================================
#     # PROFILS EN ATTENTE (validation)
#     # =====================================================
#     path("profiles/pending/", pending_profiles_list, name="pending_profiles"),
#     path("profiles/<int:profile_id>/approve/", validate_profile_view, name="profile_approve"),
#     path("profiles/<int:profile_id>/refuse/", refuse_profile_view, name="profile_refuse"),
# ]








# # dashboard/urls/__init__.py
# from django.urls import path, include
# from dashboard.views.hub import dashboard_hub_view

# app_name = "dashboard"

# urlpatterns = [
#     path("", dashboard_hub_view, name="hub"),

#     path("user/", include(("dashboard.urls.user", "dashboard_user"), namespace="user")),
#     path("vendor/", include(("dashboard.urls.vendor", "dashboard_vendor"), namespace="vendor")),
#     path("b2b/", include(("dashboard.urls.b2b", "dashboard_b2b"), namespace="b2b")),
#     path("social/", include(("dashboard.urls.social", "dashboard_social"), namespace="social")),
#     path("admin/", include(("dashboard.urls.admin", "dashboard_admin"), namespace="admin")),
# ]












# from django.urls import path, include
# from dashboard.views.hub import dashboard_hub_view

# app_name = "dashboard"

# urlpatterns = [
#     # HUB DASHBOARD (OBLIGATOIRE)
#     path("", dashboard_hub_view, name="hub"),

#     # Sous-dashboards
#     path("vendor/", include("dashboard.urls.vendor")),
# ]





# # dashboard/urls/__init__.py
# from django.urls import path, include

# urlpatterns = [
#     # Inclusion du sous-namespace Vendor (optionnel pour API / CRUD)
#     path("vendor/", include("dashboard.urls.vendor")),
# ]