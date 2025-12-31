# sogentis_apps/economic/b2b/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class B2BConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    # 🔑 CHEMIN PYTHON RÉEL
    name = "economic.b2b"

    verbose_name = _("Espace Professionnels (B2B)")
