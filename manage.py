#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    # Permet de surcharger DJANGO_SETTINGS_MODULE si besoin
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

    # Optionnel : avertit si le venv n'est pas activé
    venv = os.environ.get("VIRTUAL_ENV")
    if not venv:
        print("\033[93mAttention : l'environnement virtuel Python n'est pas activé !\033[0m")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "\nCouldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
