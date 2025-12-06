#!/bin/bash
# install_locale.sh
# Prépare les dossiers locale/ et génère les fichiers django.po pour toutes les langues

# Liste des langues
LANGS="fr en nl pt de nb sv es it ru wo sw"

echo "📂 Création des dossiers locale/ pour chaque langue..."
mkdir -p locale/{fr,en,nl,pt,de,nb,sv,es,it,ru,wo,sw}/LC_MESSAGES

echo "📝 Génération des fichiers django.po..."
for lang in $LANGS; do
    echo "➡️  Langue: $lang"
    python manage.py makemessages -l $lang
done

echo "✅ Tous les fichiers de traduction ont été créés dans locale/"
