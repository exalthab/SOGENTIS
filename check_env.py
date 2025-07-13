import os
import sys
from pathlib import Path
from decouple import config, UndefinedValueError
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent

# === Variables sensibles à masquer dans l'affichage ===
SENSITIVE_KEYS = [
    "SECRET_KEY",
    "EMAIL_HOST_PASSWORD",
    "STRIPE_SECRET_KEY",
    "STRIPE_PUBLISHABLE_KEY",
    "STRIPE_WEBHOOK_SECRET",
]

# === Variables indispensables à vérifier ===
REQUIRED_ENV_VARS = [
    "DJANGO_ENV",
    "DEBUG",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "DATABASE_URL",
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "DEFAULT_FROM_EMAIL",
    "STRIPE_SECRET_KEY",
    "STRIPE_PUBLISHABLE_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "DOMAIN",
]

def mask(value: str, visible: int = 4) -> str:
    """Masque les secrets, en montrant les derniers caractères."""
    if not value:
        return "***"
    if len(value) <= visible:
        return "*" * len(value)
    return "*" * (len(value) - visible) + value[-visible:]

def check_env():
    print("🔍 Vérification des variables d'environnement...\n")
    errors = []

    for var in REQUIRED_ENV_VARS:
        try:
            value = config(var)
            if value == "":
                raise ValueError("Valeur vide")
            displayed_value = mask(value) if var in SENSITIVE_KEYS else value
            print(f"✅ {var} = {displayed_value}")
        except (UndefinedValueError, ValueError) as e:
            errors.append(f"❌ {var} est manquant ou invalide: {e}")

    # Test parsing de DATABASE_URL
    print("\n📡 Test de connexion à la base de données (via DATABASE_URL)...")
    try:
        db_url = config("DATABASE_URL")
        parsed_db = dj_database_url.parse(db_url)
        print(f"✅ DATABASE_URL parse OK : DB = {parsed_db.get('NAME')} (host={parsed_db.get('HOST')})")
    except Exception as e:
        errors.append(f"❌ DATABASE_URL invalide : {e}")

    print("\n📄 Résultat final :")
    if errors:
        print("\n".join(errors))
        print(f"\n⛔️ {len(errors)} erreur(s) trouvée(s) dans le fichier .env")
        sys.exit(1)
    else:
        print("🎉 Toutes les variables d’environnement sont correctement définies.")

if __name__ == "__main__":
    check_env()
