#!/bin/bash
set -euo pipefail

### CONFIGURATION PERSONNALISABLE ###
PROJECT_NAME="SOGENTIS"
USER_NAME="$(whoami)"
DOMAIN="sogentis.org"
REPO_URL="https://ton-repo.git"
PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
SOCK_FILE="$PROJECT_DIR/gunicorn.sock"
NGINX_CONF="/etc/nginx/sites-available/$PROJECT_NAME"
ENV_FILE="$PROJECT_DIR/.env"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/django_error.log"
DJANGO_SETTINGS_MODULE="config.settings.settings_loader"
DB_BACKUP_DIR="$PROJECT_DIR/backups/db"
DB_BACKUP_SCRIPT="$PROJECT_DIR/scripts/backup_db.sh"
BACKUP_RETENTION=7   # Nombre de backups à garder
EMAIL_ON_FAILURE="contact@$DOMAIN"
#############################################################################

echo "🚀 Déploiement du projet '$PROJECT_NAME' sur le domaine '$DOMAIN'..."

# 0. Création des répertoires projet et scripts si nécessaires
mkdir -p "$PROJECT_DIR" "$DB_BACKUP_DIR" "$(dirname "$DB_BACKUP_SCRIPT")"

# 1. Mise à jour système et installation des paquets
echo "📦 Installation des dépendances système..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git certbot python3-certbot-nginx ufw mailutils

# 2. Récupération du code
if [[ ! -d "$PROJECT_DIR/.git" ]]; then
  echo "📁 Clonage du dépôt..."
  git clone "$REPO_URL" "$PROJECT_DIR"
else
  echo "📥 Mise à jour du dépôt..."
  cd "$PROJECT_DIR"
  git pull origin main
fi

cd "$PROJECT_DIR"

# 3. Environnement virtuel
echo "🐍 Création de l'environnement virtuel..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Vérification/création du fichier .env
if [[ ! -f "$ENV_FILE" ]]; then
  echo "🔐 Création du fichier .env (exemple)..."
  cat <<EOF > "$ENV_FILE"
DJANGO_ENV=prod
DEBUG=False
SECRET_KEY=change_this_in_prod
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DATABASE_URL=postgres://user:pass@localhost:5432/${PROJECT_NAME,,}?sslmode=require
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.infomaniak.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=contact@$DOMAIN
EMAIL_HOST_PASSWORD=YOUR_EMAIL_PASSWORD
DEFAULT_FROM_EMAIL=contact@$DOMAIN
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
DOMAIN=https://$DOMAIN
LOG_PATH=$LOG_FILE
USE_TEMPLATE_CACHING=True
EOF
  chmod 600 "$ENV_FILE"
  echo "✅ Fichier .env créé : à modifier avec les vraies valeurs."
else
  echo "ℹ️ Le fichier .env existe déjà : $ENV_FILE"
fi

# 5. Activer l'environnement virtuel + charger .env
source "$VENV_DIR/bin/activate"
export $(grep -v '^#' "$ENV_FILE" | xargs)
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# 6. Migrations et collectstatic
echo "⚙️ Migration de la base de données & collectstatic..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 7. Préparation des logs
echo "🗂️ Préparation du répertoire de logs..."
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"
sudo chown -R "$USER_NAME":www-data "$LOG_DIR"
chmod -R 750 "$LOG_DIR"
chmod 640 "$LOG_FILE"

# 8. Configuration Gunicorn
echo "🛠️ Configuration du service Gunicorn..."
sudo tee "/etc/systemd/system/$PROJECT_NAME.service" > /dev/null <<EOF
[Unit]
Description=Gunicorn for $PROJECT_NAME
After=network.target

[Service]
User=$USER_NAME
Group=www-data
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/gunicorn --access-logfile - --workers 3 --bind unix:$SOCK_FILE config.wsgi:application
Restart=on-failure
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$PROJECT_NAME"
sudo systemctl restart "$PROJECT_NAME"

# 9. Configuration Nginx
echo "🌐 Configuration Nginx..."
sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/${PROJECT_NAME}.access.log;
    error_log /var/log/nginx/${PROJECT_NAME}.error.log;

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

sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 10. Certificat SSL
echo "🔒 Configuration du certificat SSL avec Certbot..."
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m webmaster@$DOMAIN
sudo systemctl enable certbot.timer

# 11. Sécuriser le fichier .env
chmod 600 "$ENV_FILE"

# 12. Création script de backup de la base de données avec rétention + notifications mail
echo "💾 Création du script de sauvegarde PostgreSQL avec rétention et notification mail..."

cat <<EOF > "$DB_BACKUP_SCRIPT"
#!/bin/bash
set -euo pipefail

TIMESTAMP=\$(date +"%Y%m%d_%H%M")
BACKUP_FILE="$DB_BACKUP_DIR/db_\$TIMESTAMP.sql"
RETENTION=$BACKUP_RETENTION
EMAIL="$EMAIL_ON_FAILURE"

# Fonction envoi mail d'erreur via Infomaniak
send_error_mail() {
    local MSG="\$1"
    echo -e "Subject: [Backup DB] Échec de la sauvegarde\n\n\$MSG" | sendmail -v -S mail.infomaniak.com:587 -f "$EMAIL_ON_FAILURE" -au"$EMAIL_ON_FAILURE" -ap"$YOUR_EMAIL_PASSWORD" "\$EMAIL"
}

# Backup PostgreSQL
if ! pg_dump -U postgres -d ${PROJECT_NAME,,} > "\$BACKUP_FILE"; then
    send_error_mail "La sauvegarde de la base de données a échoué le \$(date)."
    exit 1
fi

# Rétention : supprimer les backups plus anciens que les $RETENTION derniers
cd "$DB_BACKUP_DIR"
BACKUPS_TO_DELETE=\$(ls -1t db_*.sql | tail -n +\$((RETENTION+1)) || true)
if [[ -n "\$BACKUPS_TO_DELETE" ]]; then
    rm -f \$BACKUPS_TO_DELETE
fi
EOF

chmod +x "$DB_BACKUP_SCRIPT"

# 13. Ajouter la tâche cron à 2h tous les jours (si pas déjà présente)
if ! crontab -l | grep -q "$DB_BACKUP_SCRIPT"; then
  echo "🕑 Planification de la sauvegarde quotidienne (2h du matin)..."
  (crontab -l 2>/dev/null; echo "0 2 * * * $DB_BACKUP_SCRIPT") | crontab -
else
  echo "ℹ️ Cron de backup déjà présent."
fi

# 14. Fin
echo ""
echo "🎉 Déploiement terminé avec succès !"
echo "➡️ Accès au site : https://$DOMAIN"
echo "📂 Logs Django : $LOG_FILE"
echo "🗄️  Backups DB dans : $DB_BACKUP_DIR"
echo "📧 Envoi d'email en cas d'échec de backup vers : $EMAIL_ON_FAILURE"
