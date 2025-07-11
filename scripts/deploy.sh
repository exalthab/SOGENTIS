#!/bin/bash

echo "📦 Déploiement SOGENTIS..."

# Étape 1 : Pull le dépôt si tu as configuré Git
# git pull origin main

# Étape 2 : Build et run les containers
docker-compose down
docker-compose build
docker-compose up -d

# Étape 3 : Migrations + collecte des fichiers statiques
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput

echo "✅ Déploiement terminé !"
