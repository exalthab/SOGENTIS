from __future__ import annotations

from django.urls import include, path

app_name = "tech"

urlpatterns = [
    path("integrations/", include(("tech.integrations.urls", "integrations"), namespace="integrations")),
    path("analytics/", include(("tech.analytics.urls", "analytics"), namespace="analytics")),
    path("ai/", include(("tech.ai.urls", "ai"), namespace="ai")),
    path("labs/", include(("tech.labs.urls", "labs"), namespace="labs")),
]
