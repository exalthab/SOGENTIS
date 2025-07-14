#!/bin/bash
set -e

################################################################################
# SOGENTIS - INSTALLATION STEP 1 : Préparation Ubuntu 22.04+ & configuration
################################################################################

PROJECT_NAME="SOGENTIS"
PROJECT_DIR="$HOME/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
VARS_FILE="$PROJECT_DIR/vars.sh"

echo -e "\n\033[1;34m===============================\033[0m"
echo -e "\033[1;34m SOGENTIS - INSTALLATION STEP 1\033[0m"
echo -e "\033[1;34m===============================\033[0m\n"

# 1. Mise à jour du système
echo "[1] 🔄 Mise à jour du système..."
sudo apt update && sudo apt -y upgrade

# 2. Installation de Python et outils venv
echo "[2] 🐍 Installation de Python 3, pip, venv..."
sudo apt -y install python3 python3-pip python3-venv

# 3. Installation virtualenv (au cas où pip le réclame)
echo "[3] 📦 Installation de virtualenv (user)..."
python3 -m pip install --user virtualenv

# 4. Création du dossier projet
echo "[4] 📁 Création du dossier projet : $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

# 5. Création de l'environnement virtuel
if [ -d "$VENV_DIR" ]; then
    echo "[5] ⚠️  L’environnement virtuel existe déjà à $VENV_DIR"
else
    echo "[5] 🌱 Création de l’environnement virtuel..."
    python3 -m venv "$VENV_DIR"
fi

# 6. Création du fichier vars.sh
if [ -f "$VARS_FILE" ]; then
    echo "[6] 📄 Fichier vars.sh déjà présent."
else
    echo "[6] 🛠️  Création du fichier de configuration : vars.sh"
    cat <<EOF > "$VARS_FILE"
#!/bin/bash

# =======================
# SOGENTIS - Configuration
# =======================

# Propriétés projet
PROJECT_NAME="SOGENTIS"
PROJECT_DIR="\$HOME/\$PROJECT_NAME"
VENV_DIR="\$PROJECT_DIR/venv"

# Base de données
DB_NAME="sogentis_db"
DB_USER="sogentis_user"
DB_PASS="ChangeMeToAStrongPassword!"   # <-- Modifier après l'installation

# Domaine et contact admin
DOMAIN="sogentis.org"
ADMIN_MAIL="admin@\$DOMAIN"

# Dépôt Git (à ajuster)
GIT_REPO_URL="https://votre-repo-git.git"   # <-- À modifier

# Format date
DATE=\$(date +%F_%H-%M)

# Sauvegardes
BACKUP_DIR_DB="\$PROJECT_DIR/backups/db"
BACKUP_DIR_MEDIA="\$PROJECT_DIR/backups/media"
BACKUP_DIR_LOGS="\$PROJECT_DIR/backups/logs"
EOF
    chmod +x "$VARS_FILE"
fi

# 7. Activation du venv
echo "[7] ✅ Activation de l’environnement virtuel..."
source "$VENV_DIR/bin/activate"

# 8. Fin
echo -e "\n\033[1;32m============ PAUSE ============\033[0m"
echo "✅ Étape 1 terminée."
echo "Vous pouvez maintenant :"
echo " - Modifier les variables dans $VARS_FILE si besoin"
echo " - Placer vos fichiers .env dans $PROJECT_DIR"
echo
echo "👉 Quand prêt, lancez :"
echo "   bash install_sogentis_step2.sh"
echo -e "\033[1;32m===============================\033[0m\n"

deactivate
exit 0
