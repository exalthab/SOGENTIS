# config/asgi.py

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

# === Définir BASE_DIR ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Ajouter sogentis_apps au PYTHONPATH ===
sys.path.insert(0, str(BASE_DIR / "sogentis_apps"))

# === Charger le fichier .env s'il existe ===
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ .env file loaded from:", env_path)
else:
    print("⚠️ Aucun fichier .env trouvé à :", env_path)

# === Définir le module de configuration Django ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

# === Lancer l'application ASGI ===
application = get_asgi_application()
