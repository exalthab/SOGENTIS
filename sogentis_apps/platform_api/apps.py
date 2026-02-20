# platform_api/apps.py
from __future__ import annotations
from django.apps import AppConfig

class PlatformAPIConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "platform_api"
    label = "platform_api"
    verbose_name = "Platform API"
