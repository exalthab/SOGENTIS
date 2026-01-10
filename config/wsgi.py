# config/wsgi.py

import os
import sys
import logging
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Base directory
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Logging minimal (compatible gunicorn / uwsgi)
# ------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Ajout du dossier sogentis_apps au PYTHONPATH (si nécessaire)
# ------------------------------------------------------------------
apps_path = BASE_DIR / "sogentis_apps"
if apps_path.exists() and str(apps_path) not in sys.path:
    sys.path.insert(0, str(apps_path))

# ------------------------------------------------------------------
# Chargement du fichier .env (optionnel – utile en local)
# ⚠️ En prod, privilégier les variables d’environnement natives
# ------------------------------------------------------------------
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info("Environment variables loaded from .env")

# ------------------------------------------------------------------
# Configuration Django
# ------------------------------------------------------------------
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.settings_loader",
)

# ------------------------------------------------------------------
# Application WSGI
# ------------------------------------------------------------------
application = get_wsgi_application()






# # config/wsgi.py

# import os
# import sys
# from pathlib import Path

# from django.core.wsgi import get_wsgi_application
# from dotenv import load_dotenv

# # === BASE DIR ===
# BASE_DIR = Path(__file__).resolve().parent.parent

# # === Ajout du dossier sogentis_apps au PYTHONPATH ===
# sys.path.insert(0, str(BASE_DIR / "sogentis_apps"))

# # === Chargement du fichier .env (si présent à la racine) ===
# env_path = BASE_DIR / ".env"
# if env_path.exists():
#     load_dotenv(dotenv_path=env_path)
#     print("✅ .env file loaded from:", env_path)
# else:
#     print("⚠️ Aucun fichier .env trouvé à :", env_path)

# # === Spécification du module de configuration Django ===
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

# # === Initialisation de l'application WSGI ===
# application = get_wsgi_application()
