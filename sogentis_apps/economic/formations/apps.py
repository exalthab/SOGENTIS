# sogentis_apps/economic/formations/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FormationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    name = "economic.formations"

    verbose_name = _("Formations en ligne")
    
    def ready(self):
        from . import signals