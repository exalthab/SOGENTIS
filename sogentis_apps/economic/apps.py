# economic/apps.py
from __future__ import annotations

from django.apps import AppConfig


class EconomicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "economic"
    verbose_name = "Economic (Hub)"
