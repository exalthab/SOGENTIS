#!/bin/bash
set -e

################################################################################
# SOGENTIS - INSTALLATION STEP 3 : Mises à jour, corrections, maintenance
################################################################################

# Chargement des variables
VARS_FILE="$HOME/SOGENTIS/vars.sh"
if [ ! -f "$VARS_FILE" ]; then
    echo "❌ Fichier de configuration $VARS_FILE manquant. Lancez d'abord l'étape 1."
    exit 1
fi
source "$VARS_FILE"

echo -e "\n\033[1;34m==========================================\033[0m"
echo -e "\033[1;34m SOGENTIS - INSTALLATION / MAINTENANCE 3\033[0m"
echo -e "\033[1;34m==========================================\033[0m\n"

# 1. Mise à jour système + Python
echo "[1] 🔄 Mise à jour système et pip..."
sudo apt update && sudo apt -y upgrade
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel
pip list --outdated

# 2. Correction permissions dossiers critiques
echo "[2] 🔧 Correction permissions dossiers (logs, static, media)..."
sudo chown -R $USER:www-data "$PROJECT_DIR"
sudo chmod -R 775 "$PROJECT_DIR/logs" "$PROJECT_DIR/static" "$PROJECT_DIR/media"

# 3. Vérification services critiques
echo "[3] ⚙️ Vérification statuts services (gunicorn, nginx, postgresql, redis, fail2ban)..."
sudo systemctl status gunicorn || true
sudo systemctl status nginx || true
sudo systemctl status postgresql || true
sudo systemctl status redis-server || true
sudo systemctl status fail2ban || true

# 4. Nettoyage paquets inutiles et cache pip
echo "[4] 🧹 Nettoyage paquets inutiles et cache pip..."
sudo apt -y autoremove
sudo apt -y autoclean
pip cache purge

# 5. Diagnostic sécurité rapide
echo "[5] 🔒 Diagnostic sécurité fail2ban, ufw, SSL..."
sudo fail2ban-client status
sudo ufw status verbose
sudo certbot certificates

# 6. Configuration logrotate
echo "[6] 📝 Configuration logrotate..."
sudo tee /etc/logrotate.d/sogentis > /dev/null <<EOF
$PROJECT_DIR/logs/*.log {
    weekly
    missingok
    rotate 8
    compress
    delaycompress
    notifempty
    create 664 $USER www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn > /dev/null 2>/dev/null || true
    endscript
}
EOF

# 7. Outils diagnostic réseau et performances
echo "[7] 🛠️ Installation outils diagnostics (net-tools, nload, iftop, iotop)..."
sudo apt -y install net-tools nload iftop iotop

# 8. Vérification configuration nginx
echo "[8] 🔍 Test configuration nginx..."
sudo nginx -t

# 9. Rechargement services critiques
echo "[9] ♻️ Rechargement nginx et redémarrage gunicorn..."
sudo systemctl reload nginx
sudo systemctl restart gunicorn

# 10. Mise à jour optionnelle node/npm/yarn (commentée)
echo "[10] ⚙️ (Optionnel) Mise à jour nodejs/npm/yarn..."
# sudo apt -y install nodejs npm
# sudo npm install -g yarn
# cd $PROJECT_DIR && yarn install --check-files

# 11. Backup manuel base PostgreSQL
echo "[11] 💾 Backup manuel base PostgreSQL..."
mkdir -p "$BACKUP_DIR_DB"
sudo -u postgres pg_dump $DB_NAME | gzip > "$BACKUP_DIR_DB/$(date +%F_%H-%M)_$DB_NAME.sql.gz"

# 12. Vérification présence fichier .env et permissions
echo "[12] 🔎 Vérification présence .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️ ATTENTION : fichier .env manquant dans $PROJECT_DIR"
else
    echo ".env présent."
    sudo chmod 660 "$PROJECT_DIR/.env"
fi

# 13. Installation atop (optionnel)
echo "[13] 📈 Installation atop..."
sudo apt -y install atop

# 14. Installation auditd (optionnel)
echo "[14] 🛡️ Installation auditd (surveillance fichiers critiques)..."
sudo apt -y install auditd

echo
echo -e "\033[1;32m===========================\033[0m"
echo -e "\033[1;32mSOGENTIS - Maintenance/Step 3 OK !\033[0m"
echo -e "Dernier diagnostic sécurité et logs effectué."
echo -e "N'oubliez pas de vérifier l’intégrité de l’app, SSL et backups."
echo -e "\033[1;32m===========================\033[0m"

deactivate
exit 0
