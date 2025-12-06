#!/usr/bin/env bash
set -euo pipefail

# Répertoire du projet (celui qui contient manage.py)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Ignore ces dossiers à l’extraction
IGNORES=(-i venv -i .venv -i node_modules -i .git -i static -i media)

echo "==> Lecture des langues depuis settings…"
LANGS=$(python - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.conf import settings
from django.utils.translation import to_locale

codes = []
for code, _ in settings.LANGUAGES:
    # normalise vers le dossier (zh-hans -> zh_Hans, pt-br -> pt_BR)
    loc = to_locale(code)
    codes.append((code, loc))
print(" ".join(f"{c}:{l}" for c,l in codes))
PY
)

# LANGS sous forme "fr:fr en:en es:es zh-hans:zh_Hans pt-br:pt_BR ..."
echo "Langues: $LANGS"

# 1) Initialiser les locales qui manquent (domaine django + djangojs)
for pair in $LANGS; do
  CODE="${pair%%:*}"
  LOCALE="${pair##*:}"

  mkdir -p "locale/${LOCALE}/LC_MESSAGES"

  echo "==> makemessages django: ${CODE} (${LOCALE})"
  python manage.py makemessages "${IGNORES[@]}" -l "${CODE}" --no-location --keep-pot

  echo "==> makemessages djangojs: ${CODE} (${LOCALE})"
  python manage.py makemessages "${IGNORES[@]}" -l "${CODE}" -d djangojs -e js,mjs --no-location --keep-pot
done

# 2) Compiler
echo "==> compilemessages"
python manage.py compilemessages

echo "✅ i18n OK. Fichiers .po mis à jour et .mo compilés."
