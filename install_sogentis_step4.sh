#!/bin/bash

################################################################################
# SOGENTIS - Backup automatique base PostgreSQL avec rotation 7 jours
# Envoie un email d'alerte sur succès/échec
################################################################################

# Chargement des variables
VARS_FILE="$HOME/SOGENTIS/vars.sh"
if [ ! -f "$VARS_FILE" ]; then
    echo "❌ Fichier de configuration $VARS_FILE manquant. Lancez d'abord l'étape 1."
    exit 1
fi
source "$VARS_FILE"

DATE=$(date +%F_%H-%M)
BACKUP_FILE="$BACKUP_DIR_DB/${DATE}_${DB_NAME}.sql.gz"

mkdir -p "$BACKUP_DIR_DB"

# Sauvegarde PostgreSQL (suppose que $DB_USER a accès via .pgpass ou export PGPASSWORD)
if pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    echo "[OK] Backup $BACKUP_FILE créé avec succès."
    echo "Backup $BACKUP_FILE OK sur $(hostname)" | mail -s "SOGENTIS: Backup réussi" "$ADMIN_MAIL"
else
    echo "[ERREUR] Backup échoué !" | mail -s "ECHEC BACKUP $DB_NAME sur $(hostname)" "$ADMIN_MAIL"
    exit 1
fi

# Rotation : supprimer backups de plus de 7 jours
find "$BACKUP_DIR_DB" -type f -name "*.sql.gz" -mtime +7 -exec rm -f {} \;

exit 0
