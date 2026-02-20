# tech/integrations/apps.py
from __future__ import annotations
from django.apps import AppConfig

class TechIntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tech.integrations"
    label = "tech_integrations"
    verbose_name = "Tech / Integrations"
