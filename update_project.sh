#!/bin/bash
set -e

PROJECT_DIR="$HOME/SOGENTIS"
VENV_DIR="$PROJECT_DIR/venv"
BRANCH="main"

echo "🔄 Mise à jour du projet depuis Git..."

cd "$PROJECT_DIR"
git fetch origin
git reset --hard origin/$BRANCH

echo "Activation de l'environnement virtuel..."
source "$VENV_DIR/bin/activate"

echo "Installation des dépendances..."
pip install -r requirements.txt

echo "Exécution des migrations Django..."
python manage.py migrate --noinput

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Redémarrage des services Gunicorn et Nginx..."
sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "✅ Mise à jour terminée avec succès."
deactivate
exit 0
