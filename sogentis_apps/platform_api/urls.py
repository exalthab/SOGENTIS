# platform_api/urls.py
from __future__ import annotations

from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("v1/economic/", include(("economic.api.urls", "economic_api"), namespace="economic")),
]

try:
    urlpatterns += [
        path("v1/tech/", include(("tech.api.urls", "tech_api"), namespace="tech")),
    ]
except Exception:
    pass
