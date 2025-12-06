#!/bin/bash
set -e

################################################################################
# SOGENTIS - INSTALLATION STEP 2 : Déploiement services et application Django
################################################################################

# Chargement des variables d’environnement
VARS_FILE="$HOME/SOGENTIS/vars.sh"
if [ ! -f "$VARS_FILE" ]; then
    echo "❌ Fichier de configuration $VARS_FILE manquant. Lancez d'abord l'étape 1."
    exit 1
fi
source "$VARS_FILE"

echo -e "\n\033[1;34m===============================\033[0m"
echo -e "\033[1;34m SOGENTIS - INSTALLATION STEP 2\033[0m"
echo -e "\033[1;34m===============================\033[0m\n"

# 1. PostgreSQL
echo "[1] 🛠️  Installation PostgreSQL..."
sudo apt -y install postgresql postgresql-contrib libpq-dev

echo "[2] 📦 Configuration base PostgreSQL..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 2. nginx + git
echo "[3] 🌐 Installation de Nginx et Git..."
sudo apt -y install nginx git

# 3. Clonage dépôt
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "[4] 🧪 Clonage dépôt GIT..."
    git clone "$GIT_REPO_URL" "$PROJECT_DIR"
else
    echo "[4] ✅ Dépôt déjà présent."
fi

# 4. Dépendances Python
echo "[5] 📦 Installation requirements Django..."
pip install --upgrade pip wheel
REQUIREMENTS_FILE="$PROJECT_DIR/$DJANGO_REQUIREMENTS"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "❌ Fichier $REQUIREMENTS_FILE introuvable"
    exit 1
fi
pip install -r "$REQUIREMENTS_FILE"
pip install gunicorn psycopg2-binary stripe celery redis

# 5. Outils système
echo "[6] 🛠️  Installation outils système..."
sudo apt -y install build-essential libssl-dev libffi-dev python3-dev htop glances

# 6. Redis
echo "[7] ⚡ Installation Redis..."
sudo apt -y install redis-server

# 7. Certbot
echo "[8] 🔒 Installation Certbot..."
sudo apt -y install certbot python3-certbot-nginx

# 8. Backups et static/media
echo "[9] 💾 Création dossiers de sauvegarde..."
mkdir -p "$BACKUP_DIR_DB" "$BACKUP_DIR_MEDIA" "$BACKUP_DIR_LOGS"
mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/media" "$PROJECT_DIR/static"

# 9. Sécurité : Fail2ban + UFW
echo "[10] 🔐 Sécurité (fail2ban, ufw, ssh)..."
sudo apt -y install fail2ban ufw
sudo systemctl enable fail2ban --now
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config || true
sudo systemctl restart sshd || true

# 10. Migrations Django
echo "[11] 🔄 Django migrate..."
cd "$PROJECT_DIR"
python manage.py migrate

# 11. Static files
echo "[12] 📁 Django collectstatic..."
python manage.py collectstatic --noinput

# 12. Gunicorn config
echo "[13] 🧩 Configuration Gunicorn (systemd)..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for $PROJECT_NAME
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn --access-logfile - --workers 3 --bind unix:$PROJECT_DIR/gunicorn.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

# 13. Nginx config
echo "[14] 🌍 Configuration Nginx..."
sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $PROJECT_DIR;
    }
    location /media/ {
        root $PROJECT_DIR;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/gunicorn.sock;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 14. Certbot HTTPS
echo "[15] 🔐 Activation HTTPS avec Certbot..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --redirect --non-interactive --agree-tos -m "$ADMIN_MAIL" || true

# FIN
echo -e "\n\033[1;32m===============================\033[0m"
echo -e "\033[1;32m SOGENTIS - Déploiement OK !\033[0m"
echo -e "\033[1;32m Accès : https://$DOMAIN\033[0m"
echo -e "\033[1;32m===============================\033[0m"

exit 0
