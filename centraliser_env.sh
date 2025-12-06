#!/bin/bash
# vars.sh - Charge automatiquement les variables depuis .env

ENV_FILE="$HOME/SOGENTIS/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Fichier .env introuvable dans $ENV_FILE"
  exit 1
fi

# Exporter toutes les variables déclarées dans .env (ignorer les commentaires et lignes vides)
export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs)
