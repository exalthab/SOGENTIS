# sogentis_apps/economic/resources/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResourcesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    name = "economic.resources"

    verbose_name = _("Centre de ressources")
