# # config/settings/modules/static.py

from pathlib import Path
from decouple import config

# BASE_DIR pointant vers /config/settings/modules/../../..
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


# ------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------
STATIC_URL = config("STATIC_URL", default="/static/")

# Dossier où collectstatic dépose les fichiers (prod)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Dossier statique principal pour le développement
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ------------------------------------------------------------
# MEDIA FILES (uploads utilisateurs + CKEditor)
# ------------------------------------------------------------
MEDIA_URL = config("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / "media"   # NE PAS mettre config()


# Créer automatiquement le dossier uploads/ pour CKEditor
UPLOADS_DIR = MEDIA_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


