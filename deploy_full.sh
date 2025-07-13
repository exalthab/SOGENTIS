#!/bin/bash

set -e

# === Configuration initiale ===
read -p "Nom du projet Django (ex: SOGENTIS): " PROJECT_NAME
read -p "Nom d'utilisateur système (par défaut: $(whoami)): " USER_INPUT
USER_NAME=${USER_INPUT:-$(whoami)}
read -p "Domaine principal (ex: sogentis.org): " DOMAIN_NAME
read -p "Autres domaines (séparés par virgule, ex: sogentis.org,www.sogentis.org): " ALLOWED_HOSTS

PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
SOCK_FILE="$PROJECT_DIR/gunicorn.sock"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_WSGI_MODULE="$PROJECT_NAME.wsgi:application"
NGINX_CONFIG="/etc/nginx/sites-available/$PROJECT_NAME"
LOGS_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOGS_DIR/django_error.log"
ENV_FILE="$PROJECT_DIR/.env"

# --- Vérification .env ---
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Le fichier $ENV_FILE n'existe pas ! Crée-le avant de lancer ce script."
  echo "Il doit contenir :"
  echo "LOG_PATH=$LOG_FILE"
  exit 1
fi

# --- Mise à jour du système ---
echo "📦 Mise à jour du serveur..."
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip nginx git build-essential libpq-dev ufw certbot python3-certbot-nginx -y

# --- Setup virtualenv ---
if [ ! -d "$VENV_DIR" ]; then
  echo "🐍 Création de l’environnement virtuel Python..."
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# --- Dépendances Python ---
echo "📦 Installation des dépendances Python..."
pip install --upgrade pip setuptools wheel
pip install -r "$PROJECT_DIR/requirements.txt"

# --- Vérification Gunicorn ---
if ! pip show gunicorn > /dev/null; then
  pip install gunicorn
fi

# --- Migration et fichiers statiques ---
cd "$PROJECT_DIR"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# --- Dossiers logs et media ---
mkdir -p "$LOGS_DIR" "$PROJECT_DIR/media"
touch "$LOG_FILE"
sudo chown -R "$USER_NAME":www-data "$LOGS_DIR" "$PROJECT_DIR/media"
sudo chmod -R 775 "$LOGS_DIR" "$PROJECT_DIR/media"
sudo chmod 664 "$LOG_FILE"

# --- Création du service systemd Gunicorn ---
echo "🔐 Création du service Gunicorn..."
sudo tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for Django project: $PROJECT_NAME
After=network.target

[Service]
User=$USER_NAME
Group=www-data
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/gunicorn --access-logfile - --workers 3 --bind unix:$SOCK_FILE $DJANGO_WSGI_MODULE
Restart=always
RestartSec=5
UMask=007

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart $PROJECT_NAME
sudo systemctl enable $PROJECT_NAME

# --- Préparation multi-domaines ---
IFS=',' read -ra DOMAINS <<< "$ALLOWED_HOSTS"
NGINX_SERVER_NAMES=""
CERTBOT_DOMAINS=""
for d in "${DOMAINS[@]}"; do
  NGINX_SERVER_NAMES="$NGINX_SERVER_NAMES $d"
  CERTBOT_DOMAINS="$CERTBOT_DOMAINS -d $d"
done

# --- Fichier TLS de Certbot si manquant ---
SSL_OPTIONS="/etc/letsencrypt/options-ssl-nginx.conf"
if [ ! -f "$SSL_OPTIONS" ]; then
  sudo wget https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf -O $SSL_OPTIONS
fi

# --- Configuration NGINX ---
echo "🌐 Génération de la configuration NGINX + SSL..."
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
        proxy_read_timeout 300;
    }
}
EOF

sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/

# --- Test NGINX ---
if ! sudo nginx -t; then
  echo "❌ Erreur dans la configuration NGINX. Abandon."
  exit 1
fi
sudo systemctl reload nginx

# --- Firewall ---
echo "🔓 Activation du firewall UFW..."
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# --- SSL avec Certbot ---
echo "🔐 Installation ou renouvellement du certificat SSL..."
sudo certbot --nginx $CERTBOT_DOMAINS --non-interactive --agree-tos -m webmaster@$DOMAIN_NAME

# --- Activation du renouvellement auto ---
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo
echo "🎉 Déploiement Django terminé avec succès !"
echo "🌐 Accède à : https://$DOMAIN_NAME"
echo "🌐 Domaines supplémentaires :$NGINX_SERVER_NAMES"
