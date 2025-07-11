import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
    # BASE_DIR / "sogentis_apps" / "social" / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
