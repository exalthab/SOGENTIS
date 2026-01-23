# search/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
    verbose_name = "Search"

    def ready(self):
        # Enregistre les signaux d'indexation
        try:
            from . import signals  # noqa: F401
        except Exception as exc:
            logger.exception("Could not import search.signals: %s", exc)





# # search/apps.py
# from django.apps import AppConfig
# import logging

# logger = logging.getLogger(__name__)

# class SearchConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "search"
#     verbose_name = "Search"

#     def ready(self):
#         # importe les signaux pour les enregistrer
#         try:
#             from . import signals  # noqa: F401
#         except Exception as exc:
#             # Ne bloque pas le démarrage si signals échoue
#             logger.exception("Could not import apps.search.signals: %s", exc)
