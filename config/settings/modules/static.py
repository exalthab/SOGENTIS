# config/settings/modules/static.py
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

STATIC_URL = config("STATIC_URL", default="/static/")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = config("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / "media"

UPLOADS_DIR = MEDIA_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# PDF ASSETS (logo / cachet / signature) + OUTPUT (QR, pdf tmp)
# ============================================================
PDF_ASSETS_SUBDIR = "pdf"  # => BASE_DIR/static/pdf/...
PDF_QR_DIR = MEDIA_ROOT / "invoices" / "qr"
PDF_QR_DIR.mkdir(parents=True, exist_ok=True)

# Optionnel: infos légales affichées en bas de facture/proforma
COMPANY_ADDRESS = config("COMPANY_ADDRESS", default="")
COMPANY_LEGAL = config("COMPANY_LEGAL", default="")  # ex: RCCM, NINEA, etc.
COMPANY_PHONE = config("COMPANY_PHONE", default="")
COMPANY_EMAIL = config("COMPANY_EMAIL", default="")
COMPANY_WEBSITE = config("COMPANY_WEBSITE", default="")





# # # config/settings/modules/static.py

# from pathlib import Path
# from decouple import config

# # BASE_DIR pointant vers /config/settings/modules/../../..
# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


# # ------------------------------------------------------------
# # STATIC FILES
# # ------------------------------------------------------------
# STATIC_URL = config("STATIC_URL", default="/static/")

# # Dossier où collectstatic dépose les fichiers (prod)
# STATIC_ROOT = BASE_DIR / "staticfiles"

# # Dossier statique principal pour le développement
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]


# # ------------------------------------------------------------
# # MEDIA FILES (uploads utilisateurs + CKEditor)
# # ------------------------------------------------------------
# MEDIA_URL = config("MEDIA_URL", default="/media/")
# MEDIA_ROOT = BASE_DIR / "media"   # NE PAS mettre config()


# # Créer automatiquement le dossier uploads/ pour CKEditor
# UPLOADS_DIR = MEDIA_ROOT / "uploads"
# UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


