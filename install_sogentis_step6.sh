#!/bin/bash

################################################################################
# SOGENTIS - Backup automatique du dossier logs/
# Conservation 7 jours, email d'alerte sur succès/échec
################################################################################

# Chargement des variables
VARS_FILE="$HOME/SOGENTIS/vars.sh"
if [ ! -f "$VARS_FILE" ]; then
    echo "❌ Fichier de configuration $VARS_FILE manquant. Lancez d'abord l'étape 1."
    exit 1
fi
source "$VARS_FILE"

DATE=$(date +%F_%H-%M)
BACKUP_FILE="$BACKUP_DIR_LOGS/logs_${DATE}.tar.gz"

mkdir -p "$BACKUP_DIR_LOGS"

# Archive logs
if tar -czf "$BACKUP_FILE" -C "$LOGS_DIR" . ; then
    echo "[OK] Backup $BACKUP_FILE créé avec succès."
    echo "Backup logs $BACKUP_FILE OK sur $(hostname)" | mail -s "SOGENTIS: Backup logs réussi" "$ADMIN_MAIL"
else
    echo "[ERREUR] Backup logs échoué !" | mail -s "ECHEC BACKUP LOGS sur $(hostname)" "$ADMIN_MAIL"
    exit 1
fi

# Rotation : SUPPRIMER les backups de + de 7 jours
find "$BACKUP_DIR_LOGS" -type f -name "*.tar.gz" -mtime +7 -exec rm -f {} \;

exit 0
