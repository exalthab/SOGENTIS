# economic/prestations/apps.py
from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PrestationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "economic.prestations"
    verbose_name = _("Prestations")





# # economic/prestations/apps.py
# from __future__ import annotations
# from django.utils.translation import gettext_lazy as _

# from django.apps import AppConfig


# class PrestationsConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "economic.prestations"
#     verbose_name = "Prestations"





# # sogentis_apps/economic/services/apps.py

# from django.apps import AppConfig
# from django.utils.translation import gettext_lazy as _


# class EconomicServicesConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"

#     name = "economic.services"

#     verbose_name = _("Services numériques")
