# /economic/ecommerce/apps.py
from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "economic.ecommerce"

    # ✅ GARDE le label historique attendu par les relations "ecommerce.X"
    label = "ecommerce"

    verbose_name = _("E-commerce")

    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass






# # /economic/ecommerce/apps.py

# from django.apps import AppConfig
# from django.utils.translation import gettext_lazy as _


# class EcommerceConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"

#     # 🔑 CHEMIN PYTHON RÉEL DU DOSSIER
#     name = "economic.ecommerce"

#     verbose_name = _("E-commerce")
    
#     def ready(self):
#         from . import signals  # noqa