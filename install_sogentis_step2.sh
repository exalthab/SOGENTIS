#!/bin/bash
set -e

################################################################################
# SOGENTIS - INSTALLATION STEP 2 : Déploiement services et application Django
################################################################################

# Chargement des variables
VARS_FILE="$HOME/SOGENTIS/vars.sh"
if [ ! -f "$VARS_FILE" ]; then
    echo "❌ Fichier de configuration $VARS_FILE manquant. Lancez d'abord l'étape 1."
    exit 1
fi
source "$VARS_FILE"

echo -e "\n\033[1;34m===============================\033[0m"
echo -e "\033[1;34m SOGENTIS - INSTALLATION STEP 2\033[0m"
echo -e "\033[1;34m===============================\033[0m\n"

# 1. Activation venv
echo "[1] ⚙️  Activation de l’environnement virtuel..."
source "$VENV_DIR/bin/activate"

# 2. Installer PostgreSQL
echo "[2] 🛠️  Installation PostgreSQL..."
sudo apt -y install postgresql postgresql-contrib libpq-dev

# 3. Création base et utilisateur
echo "[3] 📦 Configuration base PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" || echo "⚠️  Base déjà existante."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || echo "⚠️  Utilisateur déjà existant."
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 4. Installation nginx
echo "[4] 🌐 Installation de Nginx..."
sudo apt -y install nginx

# 5. Git
echo "[5] 🧬 Installation de git..."
sudo apt -y install git

# 6. Clonage dépôt
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "[6] 🧪 Clonage dépôt GIT..."
    git clone "$GIT_REPO_URL" "$PROJECT_DIR"
else
    echo "[6] ✅ Dépôt déjà présent."
fi

# 7. Installation dépendances Python
echo "[7] 📦 Installation requirements Django..."
pip install --upgrade pip wheel
REQUIREMENTS_FILE="$PROJECT_DIR/requirements/prod.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "❌ Fichier $REQUIREMENTS_FILE introuvable"
    exit 1
fi
pip install -r "$REQUIREMENTS_FILE"
pip install gunicorn psycopg2-binary stripe celery redis

# 8. Outils système utiles
echo "[8] 🛠️  Installation outils système..."
sudo apt -y install build-essential libssl-dev libffi-dev python3-dev htop glances

# 9. Redis
echo "[9] ⚡ Installation Redis..."
sudo apt -y install redis-server

# 10. Certbot
echo "[10] 🔒 Installation Certbot..."
sudo apt -y install certbot python3-certbot-nginx

# 11. Backups
echo "[11] 💾 Création dossiers de sauvegarde..."
mkdir -p "$BACKUP_DIR_DB" "$BACKUP_DIR_MEDIA" "$BACKUP_DIR_LOGS"

# 12. Logs / Media
mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/media" "$PROJECT_DIR/static"

# 13. fail2ban + ufw + SSH
echo "[12] 🔐 Sécurité (fail2ban, ufw, ssh)..."
sudo apt -y install fail2ban ufw
sudo systemctl enable fail2ban --now
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config || true
sudo systemctl restart sshd || true

# 14. Migrations
echo "[13] 🔄 Django migrations..."
cd "$PROJECT_DIR"
python manage.py migrate

# 15. Collectstatic
echo "[14] 📁 Django collectstatic..."
python manage.py collectstatic --noinput

# 16. Gunicorn config systemd
echo "[15] 🧩 Configuration Gunicorn (systemd)..."
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

# 17. Nginx config
echo "[16] 🌍 Configuration Nginx..."
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

# 18. Certbot SSL
echo "[17] 🔐 Activation HTTPS avec Certbot..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --redirect --non-interactive --agree-tos -m "$ADMIN_MAIL" || true

# FIN
echo -e "\n\033[1;32m===============================\033[0m"
echo -e "\033[1;32m SOGENTIS - Déploiement OK !\033[0m"
echo -e "\033[1;32m Accès : https://$DOMAIN\033[0m"
echo -e "\033[1;32m===============================\033[0m"

deactivate
exit 0
