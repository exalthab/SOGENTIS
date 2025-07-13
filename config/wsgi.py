# config/wsgi.py

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# === BASE DIR ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Ajout du dossier sogentis_apps au PYTHONPATH ===
sys.path.insert(0, str(BASE_DIR / "sogentis_apps"))

# === Chargement du fichier .env (si présent à la racine) ===
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ .env file loaded from:", env_path)
else:
    print("⚠️ Aucun fichier .env trouvé à :", env_path)

# === Spécification du module de configuration Django ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

# === Initialisation de l'application WSGI ===
application = get_wsgi_application()
