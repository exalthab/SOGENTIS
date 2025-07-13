# config/settings/modules/static.py

import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# URLs pour servir les fichiers statiques et média
STATIC_URL = config("STATIC_URL", default="/static/")
MEDIA_URL = config("MEDIA_URL", default="/media/")

# Répertoires où collectstatic va copier les fichiers statiques (production)
STATIC_ROOT = Path(config("STATIC_ROOT", default=BASE_DIR / "staticfiles"))

# Répertoires additionnels pour les fichiers statiques (dev principalement)
STATICFILES_DIRS = [
    BASE_DIR / "static",
    # Ajoute ici d'autres dossiers statiques spécifiques si besoin
    # Ex: BASE_DIR / "sogentis_apps" / "social" / "static",
]

# Répertoire pour les fichiers médias uploadés par les utilisateurs
MEDIA_ROOT = Path(config("MEDIA_ROOT", default=BASE_DIR / "media"))

# Optionnel : si tu utilises AWS S3 ou autre stockage externe, STATIC_URL et MEDIA_URL seront redéfinis en prod

