#!/bin/bash

################################################################################
# SOGENTIS - Backup automatique du dossier media/ (uploads, images, ...)
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
BACKUP_FILE="$BACKUP_DIR_MEDIA/media_${DATE}.tar.gz"

mkdir -p "$BACKUP_DIR_MEDIA"

# Création de l'archive
if tar -czf "$BACKUP_FILE" -C "$MEDIA_DIR" . ; then
    echo "[OK] Backup $BACKUP_FILE créé avec succès."
    echo "Backup média $BACKUP_FILE OK sur $(hostname)" | mail -s "SOGENTIS: Backup media réussi" "$ADMIN_MAIL"
else
    echo "[ERREUR] Backup media échoué !" | mail -s "ECHEC BACKUP MEDIA sur $(hostname)" "$ADMIN_MAIL"
    exit 1
fi

# Rotation : SUPPRIMER les backups de + de 7 jours
find "$BACKUP_DIR_MEDIA" -type f -name "*.tar.gz" -mtime +7 -exec rm -f {} \;

exit 0
