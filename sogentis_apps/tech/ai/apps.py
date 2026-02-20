# tech/ai/apps.py
from __future__ import annotations
from django.apps import AppConfig

class TechAIConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tech.ai"
    label = "tech_ai"
    verbose_name = "Tech / AI"
