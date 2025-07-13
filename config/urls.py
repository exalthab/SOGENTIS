from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Core app
    path('', include(('core.urls', 'core'), namespace='core')),

    # Accounts API
    path("accounts/api/", include(("accounts_users.api.urls", "accounts_users_api"), namespace="accounts_users_api")),

    # Accounts web views
    path("accounts/web/", include(("accounts_users.web.urls", "accounts_users_web"), namespace="accounts_users_web")),

    # General accounts
    path("accounts/", include("accounts_users.urls")),

    # Dashboard
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

    # Social module
    path("social/", include(("social.urls", "social"), namespace="soci")),

    # Economic modules
    path("econ/", include(("economic.urls", "econ"), namespace="econ")),
    path("ecommerce/", include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
    path("formations/", include(("economic.formations.urls", "formations"), namespace="formations")),
    path("services/", include(("economic.gestion_projets.urls", "services"), namespace="services")),

    # Stakeholders
    path("stakeholders/", include(("stakeholders.urls", "stakeholders"), namespace="stakeholders")),
]

# Serve media files only if in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (for production)
handler404 = "core.views.handler404"
handler403 = "core.views.handler403"
handler500 = "core.views.handler500"
