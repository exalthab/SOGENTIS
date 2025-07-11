#!/bin/bash

# === Configuration de base ===
ENV_FILE=".env"

echo "🛠 Génération du fichier .env de production..."
echo

# === Interactions ===
read -p "➤ Clé secrète Django (SECRET_KEY) : " SECRET_KEY
read -p "➤ Domaine autorisé (ex: sogentis.org,www.sogentis.org) : " ALLOWED_HOSTS
read -p "➤ URL de la base de données (postgres://USER:PASSWORD@HOST:PORT/DBNAME) : " DATABASE_URL
read -p "➤ Email d’envoi (EMAIL_HOST_USER) : " EMAIL_USER
read -sp "➤ Mot de passe email (EMAIL_HOST_PASSWORD) : " EMAIL_PASSWORD
echo
read -p "➤ Email expéditeur par défaut (DEFAULT_FROM_EMAIL) : " DEFAULT_FROM_EMAIL
read -p "➤ Utiliser AWS S3 ? (y/N) : " USE_S3_INPUT
USE_S3=$( [[ "$USE_S3_INPUT" =~ ^[Yy]$ ]] && echo "True" || echo "False" )

# Si S3 est activé, demander les variables
if [[ "$USE_S3" == "True" ]]; then
    read -p "➤ AWS_ACCESS_KEY_ID : " AWS_KEY
    read -p "➤ AWS_SECRET_ACCESS_KEY : " AWS_SECRET
    read -p "➤ AWS_STORAGE_BUCKET_NAME : " AWS_BUCKET
fi

# === Écriture du fichier ===
cat > "$ENV_FILE" <<EOF
# ========================
# ENVIRONNEMENT
# ========================
DJANGO_ENV=prod
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$ALLOWED_HOSTS

# ========================
# BASE DE DONNÉES
# ========================
DATABASE_URL=$DATABASE_URL

# ========================
# EMAIL (SMTP)
# ========================
EMAIL_HOST=smtp.infomaniak.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=$EMAIL_USER
EMAIL_HOST_PASSWORD=$EMAIL_PASSWORD
DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL

# ========================
# REDIS (cache et Celery)
# ========================
REDIS_URL=redis://localhost:6379/1

# ========================
# AWS S3 (optionnel)
# ========================
USE_S3=$USE_S3
EOF

# Ajout S3 si activé
if [[ "$USE_S3" == "True" ]]; then
    cat >> "$ENV_FILE" <<EOF
AWS_ACCESS_KEY_ID=$AWS_KEY
AWS_SECRET_ACCESS_KEY=$AWS_SECRET
AWS_STORAGE_BUCKET_NAME=$AWS_BUCKET
EOF
fi

# Autres variables
cat >> "$ENV_FILE" <<EOF

# ========================
# LOGGING (optionnel)
# ========================
DJANGO_LOG_DIR=/var/log/sogen

# ========================
# SENTRY (optionnel)
# ========================
# SENTRY_DSN=https://your-sentry-dsn
EOF

echo
echo "✅ Fichier .env généré avec succès : $ENV_FILE"
