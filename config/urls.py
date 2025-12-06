# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.i18n import set_language, JavaScriptCatalog
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.i18n import set_language

from core.views.lang import switch_language
from core.views.debug import lang_debug  # optionnel

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("ckeditor/", include("ckeditor_uploader.urls")), #pas nécessaire si CKEditor 5

    # ✔️ CKEditor5 upload + browse
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # i18n utilitaires (hors préfixe de langue)
    path("i18n/setlang/", set_language, name="set_language"),
    path("i18n/switch/", switch_language, name="switch_language"),
    path('i18n/', include('django.conf.urls.i18n')),  # nécessaire pour {% url 'set_language' %}
    path("lang/switch/", include("core.urls_lang")),  # ton module custom-24/10/2025

    # Catalogue JS (gettext/ngettext côté JavaScript)
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),

    # Debug (hors préfixe)
    path("debug/lang/", lang_debug, name="lang_debug"),

    # Auth (hors i18n — OK)
    path("logout/", auth_views.LogoutView.as_view(next_page="social:index"), name="logout"),

    # Accounts (souvent hors i18n)
    path("accounts/api/", include(("accounts_users.api.urls", "accounts_users_api"), namespace="accounts_users_api")),
    path("accounts/web/", include(("accounts_users.web.urls", "accounts_users_web"), namespace="accounts_users_web")),
    path("accounts/", include("accounts_users.urls")),
]

# Routes “front” sous i18n_patterns pour porter la langue dans l’URL
urlpatterns += i18n_patterns(
    path("", include(("core.urls", "core"), namespace="core")),
    path("social/", include(("social.urls", "social"), namespace="social")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("econ/", include(("economic.urls", "econ"), namespace="econ")),
    path("ecommerce/", include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
    path("formations/", include(("economic.formations.urls", "formations"), namespace="formations")),
    path("services/", include(("economic.gestion_projets.urls", "services"), namespace="services")),
    path("stakeholders/", include(("stakeholders.urls", "stakeholders"), namespace="stakeholders")),
    # path("documents/", include("documents.urls")),
    path('search/', include('search.urls', namespace='search')),
    path("", include("donations.urls", namespace="donations")),
    path("about/", include("about.urls", namespace="about")),
    
    prefix_default_language=False,  # pas de /fr/ quand FR est la langue par défaut
)

# Fichiers médias en dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Handlers d'erreurs
handler403 = "core.views.views.handler403"
handler404 = "core.views.views.handler404"
handler500 = "core.views.views.handler500"


