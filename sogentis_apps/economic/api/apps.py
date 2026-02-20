# economic/api/apps.py
from __future__ import annotations

from django.apps import AppConfig


class EconomicApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "economic.api"
    verbose_name = "Economic API"
