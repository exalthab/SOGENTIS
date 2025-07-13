#!/bin/bash

set -e

# === 1. Génération interactive du .env ===
ENV_FILE=".env"
echo "🛠 Génération du fichier .env de production..."

read -p "➤ Clé secrète Django (SECRET_KEY) : " SECRET_KEY
read -p "➤ Domaine principal (ex: sogentis.org) : " DOMAIN_NAME
read -p "➤ Autres domaines (séparés par virgule, ex: sogentis.org,www.sogentis.org,sogentis.com,sogentis.sn) : " ALLOWED_HOSTS
read -p "➤ URL de la base de données (postgres://USER:PASSWORD@HOST:PORT/DBNAME) : " DATABASE_URL
read -p "➤ Email d’envoi (EMAIL_HOST_USER) : " EMAIL_USER
read -sp "➤ Mot de passe email (EMAIL_HOST_PASSWORD) : " EMAIL_PASSWORD
echo
read -p "➤ Email expéditeur par défaut (DEFAULT_FROM_EMAIL) : " DEFAULT_FROM_EMAIL

echo
read -p "➤ Utiliser le mode SANDBOX pour les paiements (tests) ? (y/N) : " USE_SANDBOX_INPUT
USE_SANDBOX=$( [[ "$USE_SANDBOX_INPUT" =~ ^[Yy]$ ]] && echo "True" || echo "False" )

# --- STRIPE ---
echo
read -p "➤ Stripe Secret Key : " STRIPE_SECRET_KEY
read -p "➤ Stripe Publishable Key : " STRIPE_PUBLISHABLE_KEY
read -p "➤ Stripe Webhook Secret : " STRIPE_WEBHOOK_SECRET

# --- PAYPAL ---
echo
read -p "➤ PayPal Client ID : " PAYPAL_CLIENT_ID
read -p "➤ PayPal Secret : " PAYPAL_SECRET

# --- ORANGEMONEY / WAVE / VISA ---
echo
read -p "➤ OrangeMoney API Key : " ORANGE_MONEY_API_KEY
read -p "➤ Wave API Key : " WAVE_API_KEY
read -p "➤ VISA Merchant ID : " VISA_MERCHANT_ID
read -p "➤ VISA API Key : " VISA_API_KEY

read -p "➤ Utiliser AWS S3 ? (y/N) : " USE_S3_INPUT
USE_S3=$( [[ "$USE_S3_INPUT" =~ ^[Yy]$ ]] && echo "True" || echo "False" )
read -p "➤ Nom du projet Django (dossier principal, ex: SOGENTIS) : " PROJECT_NAME
read -p "➤ Chemin utilisateur système (par défaut: $(whoami)) : " USER_INPUT
USER_NAME=${USER_INPUT:-$(whoami)}
read -p "➤ URL du dépôt Git (ex: https://github.com/exalthab/SOGENTIS.git) : " REPO_URL

if [[ "$USE_S3" == "True" ]]; then
    read -p "➤ AWS_ACCESS_KEY_ID : " AWS_KEY
    read -p "➤ AWS_SECRET_ACCESS_KEY : " AWS_SECRET
    read -p "➤ AWS_STORAGE_BUCKET_NAME : " AWS_BUCKET
fi

cat > "$ENV_FILE" <<EOF
DJANGO_ENV=prod
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$ALLOWED_HOSTS
DATABASE_URL=$DATABASE_URL

EMAIL_HOST=smtp.infomaniak.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=$EMAIL_USER
EMAIL_HOST_PASSWORD=$EMAIL_PASSWORD
DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL

# Paiements
USE_SANDBOX=$USE_SANDBOX

# Stripe
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET

# PayPal
PAYPAL_CLIENT_ID=$PAYPAL_CLIENT_ID
PAYPAL_SECRET=$PAYPAL_SECRET

# Orange Money
ORANGE_MONEY_API_KEY=$ORANGE_MONEY_API_KEY

# Wave
WAVE_API_KEY=$WAVE_API_KEY

# VISA
VISA_MERCHANT_ID=$VISA_MERCHANT_ID
VISA_API_KEY=$VISA_API_KEY

REDIS_URL=redis://localhost:6379/1
USE_S3=$USE_S3
EOF

if [[ "$USE_S3" == "True" ]]; then
    cat >> "$ENV_FILE" <<EOF
AWS_ACCESS_KEY_ID=$AWS_KEY
AWS_SECRET_ACCESS_KEY=$AWS_SECRET
AWS_STORAGE_BUCKET_NAME=$AWS_BUCKET
EOF
fi

cat >> "$ENV_FILE" <<EOF

DJANGO_LOG_DIR=/var/log/$PROJECT_NAME
# SENTRY_DSN=https://your-sentry-dsn
EOF

echo "✅ Fichier .env généré : $ENV_FILE"
echo

# === 2. Déploiement projet complet ===
PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
SOCK_FILE="$PROJECT_DIR/gunicorn.sock"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_WSGI_MODULE="$PROJECT_NAME.wsgi:application"

echo "📦 Mise à jour du serveur..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installation des dépendances système..."
sudo apt install python3 python3-venv python3-pip nginx git build-essential libpq-dev ufw -y

echo "📁 Création du dossier projet..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "🔁 Clonage ou mise à jour du dépôt Git..."
if [ -d ".git" ]; then
    echo "Le dépôt Git existe déjà, mise à jour..."
    git pull || { echo "Mise à jour git échouée !"; exit 1; }
else
    git clone "$REPO_URL" . || { echo "Clonage échoué !"; exit 1; }
fi

echo "🐍 Création de l'environnement virtuel..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "📦 Installation des dépendances Python..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

cp "$ENV_FILE" "$PROJECT_DIR/.env"

echo "⚙️ Migration et collecte des fichiers statiques..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# --- Logs ---
LOGS_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOGS_DIR/django_error.log"
mkdir -p "$LOGS_DIR"
touch "$LOG_FILE"
sudo chown -R "$USER_NAME":www-data "$LOGS_DIR"
sudo chmod -R 775 "$LOGS_DIR"
sudo chmod 664 "$LOG_FILE"

# --- Systemd Gunicorn ---
echo "🔐 Création du service Gunicorn..."
sudo tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for Django project: $PROJECT_NAME
After=network.target

[Service]
User=$USER_NAME
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn --access-logfile - --workers 3 --bind unix:$SOCK_FILE $DJANGO_WSGI_MODULE

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart $PROJECT_NAME
sudo systemctl enable $PROJECT_NAME

# === Multi-domaines pour NGINX/Certbot ===
IFS=',' read -ra DOMAINS <<< "$ALLOWED_HOSTS"
NGINX_SERVER_NAMES=""
CERTBOT_DOMAINS=""
for d in "${DOMAINS[@]}"; do
  NGINX_SERVER_NAMES="$NGINX_SERVER_NAMES $d"
  CERTBOT_DOMAINS="$CERTBOT_DOMAINS -d $d"
done

NGINX_CONFIG="/etc/nginx/sites-available/$PROJECT_NAME"

echo "🌐 Génération de la config Nginx + SSL (multi-domaine)..."
sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
server {
    listen 80;
    server_name$NGINX_SERVER_NAMES;
    return 301 https://\$host\$request_uri;
}
server {
    listen 443 ssl http2;
    server_name$NGINX_SERVER_NAMES;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    access_log /var/log/nginx/${PROJECT_NAME}.access.log;
    error_log /var/log/nginx/${PROJECT_NAME}.error.log;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }
    location /media/ {
        alias $PROJECT_DIR/media/;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:$SOCK_FILE;
    }
    proxy_read_timeout 300;
}
EOF

sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# --- Firewall ---
echo "🔓 Activation du firewall (UFW)..."
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# --- Certbot SSL ---
echo "🔐 Installation de Certbot (HTTPS)..."
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx $CERTBOT_DOMAINS --non-interactive --agree-tos -m webmaster@$DOMAIN_NAME

echo "🕓 Activation du renouvellement auto SSL..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo
echo "🎉 Déploiement Django terminé !"
echo "🌐 Accède à : https://$DOMAIN_NAME"
echo "🌐 Ou sur les domaines secondaires : $NGINX_SERVER_NAMES"
