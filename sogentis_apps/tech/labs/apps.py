# tech/labs/apps.py
from __future__ import annotations
from django.apps import AppConfig

class TechLabsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tech.labs"
    label = "tech_labs"
    verbose_name = "Tech / Labs"
