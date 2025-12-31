# sogentis_apps/economic/services/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EconomicServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    name = "economic.services"

    verbose_name = _("Services numériques")
