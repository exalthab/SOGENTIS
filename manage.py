#!/usr/bin/env python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Run administrative tasks with env management and debug info."""

    BASE_DIR = Path(__file__).resolve().parent

    # Charger .env s'il existe à la racine du projet
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print(f"✅ Fichier .env chargé depuis : {env_file}")
    else:
        print(f"⚠️ Aucun fichier .env trouvé à : {env_file}")

    # Définir DJANGO_SETTINGS_MODULE si pas déjà défini
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

    # Optionnel : alerte si le virtualenv n’est pas activé
    if not os.environ.get("VIRTUAL_ENV"):
        print("\033[93m⚠️  Attention : l’environnement virtuel Python n’est pas activé !\033[0m")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "\n❌ Django est introuvable. Vérifie si :\n"
            "- Il est installé (`pip install -r requirements.txt`)\n"
            "- Le virtualenv est activé\n"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
