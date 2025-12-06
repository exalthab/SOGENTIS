#!/bin/bash

# Charger les variables depuis le fichier .env
set -a
source "$(dirname "$0")/.env"
set +a

# Affichage de vérification
echo "[INFO] Variables d'environnement chargées depuis .env"
echo " - PROJECT_NAME=$PROJECT_NAME"
echo " - PROJECT_DIR=$PROJECT_DIR"
echo " - VENV_DIR=$VENV_DIR"
echo " - DB_NAME=$DB_NAME"
echo " - DOMAIN=$DOMAIN"
