# about/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'about'
    verbose_name = "À propos"

    def ready(self):
        """
        Méthode appelée automatiquement quand l'application est chargée.
        Tu peux y importer des signaux, initialisations, etc.
        Exemple :
            from . import signals
        """
        try:
            # Importation des signaux (facultatif)
            import z_about_old.signals  # noqa: F401
            # from . import signals  # crée le fichier signals.py si tu veux l’utiliser
        except ImportError:
            pass





# # about/apps.py
# from django.apps import AppConfig

# class AboutConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'about'
#     verbose_name = "À propos"
