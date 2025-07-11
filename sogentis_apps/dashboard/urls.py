#dashboard/urls.py
from django.urls import path
from dashboard.views import index, profile, stats, dons, engagements, lists
from dashboard.views import notes

app_name = "dashboard"

urlpatterns = [
    # 🏠 Accueil du dashboard
    path("", index.dashboard_index_view, name="index"),

    # 👤 Profil utilisateur
    path("profile/", profile.dashboard_profile_view, name="profile"),

    # 📊 Statistiques
    path("stats/", stats.dashboard_stats_view, name="stats"),

    # 📋 Historique des engagements
    path("engagements/", engagements.dashboard_engagements_list_view, name="engagements_list"),

    # 💝 Historique des dons
    path("dons/", dons.dashboard_dons_list_view, name="dons_list"),

    # 📋 Listes diverses
    path("lists/", lists.dashboard_lists_view, name="lists"),

    path("notes/", notes.note_list_view, name="notes_list"),
    path("notes/create/", notes.create_note_view, name="create_note"),
    path("notes/<int:pk>/edit/", notes.edit_note_view, name="edit_note"),

]



# urlpatterns = [
#     # 🏠 Accueil du dashboard
#     path("", views.dashboard_index_view, name="index"),

#     # 👤 Profil utilisateur
#     path("profile/", views.dashboard_profile_view, name="profile"),

#     # 📊 Statistiques
#     path("stats/", views.dashboard_stats_view, name="stats"),

#     # 📋 Historique des engagements
#     path("engagements/", views.engagements_list_view, name="engagements_list"),

#     # 💝 Historique des dons
#     path("dons/", views.dons_list_view, name="dons_list"),
# ]


# urlpatterns = [
    # path("", index.dashboard_index_view, name="index"),
    # path("profile/", profile.dashboard_profile_view, name="profile"),
    # path("stats/", stats.dashboard_stats_view, name="stats"),
    # path("dons/", dons.dons_list_view, name="dons"),
    # path("engagements/", engagements.engagements_list_view, name="engagements"),
    # path("lists/", lists.dashboard_lists_view, name="lists"),
# ]
