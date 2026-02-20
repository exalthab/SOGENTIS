# tech/analytics/apps.py
from __future__ import annotations
from django.apps import AppConfig

class TechAnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tech.analytics"
    label = "tech_analytics"
    verbose_name = "Tech / Analytics"
