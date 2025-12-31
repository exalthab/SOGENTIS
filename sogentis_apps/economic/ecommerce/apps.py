# sogentis_apps/economic/ecommerce/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    # 🔑 CHEMIN PYTHON RÉEL DU DOSSIER
    name = "economic.ecommerce"

    verbose_name = _("E-commerce")
