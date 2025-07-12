#!/bin/bash

# === À PERSONNALISER ===
PROJECT_NAME="SOGENTIS"
DOMAIN_NAME="sogentis.org"
USER_NAME="$USER"
PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
REPO_URL="https://github.com/exalthab/SOGENTIS.git"
SOCK_FILE="$PROJECT_DIR/gunicorn.sock"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_WSGI_MODULE="config.wsgi:application"    # adapter si différent

echo "📦 Mise à jour du serveur..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installation des dépendances système..."
sudo apt install python3 python3-venv python3-pip nginx git build-essential libpq-dev ufw -y

echo "📁 Création du dossier projet..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "🔁 Clonage du dépôt Git..."
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

# --- .env ---
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  ATTENTION : Le fichier .env n'existe pas. Pense à le créer avec les vraies valeurs production !"
    echo "Exemple de .env :"
    cat <<'EODE'
DEBUG=False
SECRET_KEY=votre_cle_secrete
ALLOWED_HOSTS=sogentis.org,www.sogentis.org,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/sogentis_db
STRIPE_SECRET_KEY=sk_live_xxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxx
EMAIL_HOST=mail.infomaniak.com
EMAIL_HOST_USER=contact@sogentis.org
EMAIL_HOST_PASSWORD=********
LOG_PATH=$PROJECT_DIR/logs/django_error.log
EODE
fi

echo "⚙️ Migration et collecte des fichiers statiques..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# --- LOGS ---
LOGS_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOGS_DIR/django_error.log"
mkdir -p "$LOGS_DIR"
touch "$LOG_FILE"
sudo chown -R "$USER_NAME":www-data "$LOGS_DIR"
sudo chmod -R 775 "$LOGS_DIR"
sudo chmod 664 "$LOG_FILE"

# --- SYSTEMD (GUNICORN) ---
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

# --- NGINX ---
echo "🌐 Configuration Nginx..."
sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

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
}
EOF

sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# --- FIREWALL ---
echo "🔓 Configuration du firewall (UFW)..."
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# --- CERTBOT ---
echo "🔐 Installation de Certbot (HTTPS)..."
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos -m webmaster@$DOMAIN_NAME

echo "✅ Déploiement terminé ! Accède au site : https://$DOMAIN_NAME"
