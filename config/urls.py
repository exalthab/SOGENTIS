# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.i18n import i18n_patterns

# Custom views
from core.views.lang import switch_language
from core.views.debug import lang_debug


# ===========================================================
# ROUTES HORS I18N (ne changent jamais avec la langue)
# ===========================================================
urlpatterns = [
    # ─── Admin ───────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ─── CKEditor 5 ──────────────────────────────────────────
    path("ckeditor5/", include("django_ckeditor_5.urls")),

    # ─── Django i18n (POST /i18n/setlang/) ───────────────────
    path("i18n/", include("django.conf.urls.i18n")),

    # ─── Custom GET language switch ──────────────────────────
    path("i18n/switch/", switch_language, name="switch_language"),

    # ─── Ancien module langue (si encore utilisé) ────────────
    path("lang/switch/", include("core.urls_lang")),

    # ─── JavaScript translations ─────────────────────────────
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),

    # ─── Debug langue (optionnel) ────────────────────────────
    path("debug/lang/", lang_debug, name="lang_debug"),

    # ─── Authentication (hors i18n) ──────────────────────────
    # IMPORTANT : next_page doit être une URL résolue (pas un name dans i18n_patterns)
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("core:home")),
        name="logout",
    ),

    # ─── Accounts API (hors i18n) ────────────────────────────
    path(
        "accounts/api/",
        include(("accounts_users.api.urls", "accounts_users_api"), namespace="accounts_users_api"),
    ),

    # ─── Accounts (général) (hors i18n) ──────────────────────
    path("accounts/", include("accounts_users.urls")),
]


# ===========================================================
# ROUTES AVEC I18N (préfixées /fr/ /en/ …)
# ===========================================================
urlpatterns += i18n_patterns(
    # Core
    path("", include(("core.urls", "core"), namespace="core")),

    # Modules
    path("social/", include(("social.urls", "social"), namespace="social")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("economic/", include(("economic.urls", "economic"), namespace="economic")),
    path("institution/", include(("institution.urls", "institution"), namespace="institution")),

    path("stakeholders/", include(("stakeholders.urls", "stakeholders"), namespace="stakeholders")),
    path("search/", include(("search.urls", "search"), namespace="search")),
    path("", include(("donations.urls", "donations"), namespace="donations")),
    path("about/", include(("about.urls", "about"), namespace="about")),

    # Accounts web (UI) en i18n
    path(
        "accounts/web/",
        include(("accounts_users.web.urls", "accounts_users_web"), namespace="accounts_users_web"),
    ),

    prefix_default_language=False,
)


# ===========================================================
# FICHIERS MEDIA EN DEV (Nginx gère en production)
# ===========================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ===========================================================
# HANDLERS D'ERREURS
# ===========================================================
handler400 = "core.views.views.handler400"
handler403 = "core.views.views.handler403"
handler404 = "core.views.views.handler404"
handler500 = "core.views.views.handler500"







# # config/urls.py 05/01/2026

# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.contrib.auth import views as auth_views
# from django.urls import path, include
# from django.views.i18n import JavaScriptCatalog
# from django.conf.urls.i18n import i18n_patterns

# # Custom views
# from core.views.lang import switch_language
# from core.views.debug import lang_debug


# # ===========================================================
# # ROUTES HORS I18N (ne changent jamais en fonction de la langue)
# # ===========================================================
# urlpatterns = [

#     # ─── Admin ───────────────────────────────────────────────
#     path("admin/", admin.site.urls),

#     # ─── CKEditor 5 ───────────────────────────────────────────
#     path("ckeditor5/", include("django_ckeditor_5.urls")),

#     # ─── Django i18n (inclut /i18n/setlang/) ─────────────────
#     # Fournit automatiquement :
#     #   POST /i18n/setlang/     (vue set_language)
#     path("i18n/", include("django.conf.urls.i18n")),

#     # ─── Custom GET language switch ───────────────────────────
#     # Fiable même en prod avec headers stricts (Infomaniak, HSTS…)
#     path("i18n/switch/", switch_language, name="switch_language"),

#     # ─── Ancien module langue (si encore utilisé) ─────────────
#     path("lang/switch/", include("core.urls_lang")),

#     # ─── JavaScript translations ─────────────────────────────
#     path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),

#     # ─── Debug langue (optionnel) ─────────────────────────────
#     path("debug/lang/", lang_debug, name="lang_debug"),

#     # ─── Authentication (hors i18n) ───────────────────────────
#     path(
#         "logout/",
#         auth_views.LogoutView.as_view(next_page="social:index"),
#         name="logout"
#     ),

#     # ─── Accounts (API / Web / core) ─────────────────────────
#     path(
#         "accounts/api/",
#         include(("accounts_users.api.urls", "accounts_users_api"), namespace="accounts_users_api")
#     ),

#     path("accounts/", include("accounts_users.urls")),
#     # path("webhooks/<str:provider>/", ecommerce_payments.webhook_generic, name="webhook_generic"),

# ]


# # ===========================================================
# # ROUTES AVEC I18N (préfixées par /fr/ ou /en/ selon la langue)
# # ===========================================================
# urlpatterns += i18n_patterns(

#     # Core
#     path("", include(("core.urls", "core"), namespace="core")),

#     # Modules
#     path("social/", include(("social.urls", "social"), namespace="social")),
#     path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
#     path("economic/", include(("economic.urls", "economic"), namespace="economic")),
#     # path("econ/", include(("economic.urls", "economic"), namespace="economic")),

#     # path("ecommerce/", include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
#     # path("formations/", include(("economic.formations.urls", "formations"), namespace="formations")),
#     # path("services/", include(("economic.gestion_projets.urls", "services"), namespace="services")),
#     path("stakeholders/", include(("stakeholders.urls", "stakeholders"), namespace="stakeholders")),
#     path("search/", include("search.urls", namespace="search")),
#     path("", include("donations.urls", namespace="donations")),
#     path("about/", include("about.urls", namespace="about")),

#     path(
#         "accounts/web/",
#         include(("accounts_users.web.urls", "accounts_users_web"), namespace="accounts_users_web")
#     ),
#     prefix_default_language=False,
# )


# # ===========================================================
# # FICHIERS MEDIA EN MODE DEV (Nginx gère en production)
# # ===========================================================
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# # ===========================================================
# # HANDLERS D'ERREURS
# # ===========================================================
# handler400 = "core.views.views.handler400"
# handler403 = "core.views.views.handler403"
# handler404 = "core.views.views.handler404"
# handler500 = "core.views.views.handler500"





# # config/urls.py
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.contrib.auth import views as auth_views
# from django.urls import path, include
# from django.views.i18n import set_language, JavaScriptCatalog
# from django.conf.urls.i18n import i18n_patterns
# from django.conf.urls.i18n import set_language

# from core.views.lang import switch_language
# from core.views.debug import lang_debug  # optionnel

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     # path("ckeditor/", include("ckeditor_uploader.urls")), #pas nécessaire si CKEditor 5

#     # ✔️ CKEditor5 upload + browse
#     path("ckeditor5/", include('django_ckeditor_5.urls')),

#     # i18n utilitaires (hors préfixe de langue)
#     path("i18n/setlang/", set_language, name="set_language"),
#     path("i18n/switch/", switch_language, name="switch_language"),
#     path('i18n/', include('django.conf.urls.i18n')),  # nécessaire pour {% url 'set_language' %}
#     path("lang/switch/", include("core.urls_lang")),  # ton module custom-24/10/2025

#     # Catalogue JS (gettext/ngettext côté JavaScript)
#     path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),

#     # Debug (hors préfixe)
#     path("debug/lang/", lang_debug, name="lang_debug"),

#     # Auth (hors i18n — OK)
#     path("logout/", auth_views.LogoutView.as_view(next_page="social:index"), name="logout"),

#     # Accounts (souvent hors i18n)
#     path("accounts/api/", include(("accounts_users.api.urls", "accounts_users_api"), namespace="accounts_users_api")),
#     path("accounts/web/", include(("accounts_users.web.urls", "accounts_users_web"), namespace="accounts_users_web")),
#     path("accounts/", include("accounts_users.urls")),
# ]

# # Routes “front” sous i18n_patterns pour porter la langue dans l’URL
# urlpatterns += i18n_patterns(
#     path("", include(("core.urls", "core"), namespace="core")),
#     path("social/", include(("social.urls", "social"), namespace="social")),
#     path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
#     path("econ/", include(("economic.urls", "econ"), namespace="econ")),
#     path("ecommerce/", include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
#     path("formations/", include(("economic.formations.urls", "formations"), namespace="formations")),
#     path("services/", include(("economic.gestion_projets.urls", "services"), namespace="services")),
#     path("stakeholders/", include(("stakeholders.urls", "stakeholders"), namespace="stakeholders")),
#     # path("documents/", include("documents.urls")),
#     path('search/', include('search.urls', namespace='search')),
#     path("", include("donations.urls", namespace="donations")),
#     path("about/", include("about.urls", namespace="about")),
    
#     prefix_default_language=False,  # pas de /fr/ quand FR est la langue par défaut
# )

# # Fichiers médias en dev
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # Handlers d'erreurs
# handler403 = "core.views.views.handler403"
# handler404 = "core.views.views.handler404"
# handler500 = "core.views.views.handler500"


