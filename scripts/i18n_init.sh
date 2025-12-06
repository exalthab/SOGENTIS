#!/usr/bin/env bash
# Initialize and compile Django i18n locales for multiple languages.
# Usage:
#   ./scripts/i18n_init.sh                 # utilise la liste par défaut
#   ./scripts/i18n_init.sh fr en wo        # ou passe les langues en argument
#   LANGS="fr en es" ./scripts/i18n_init.sh

set -euo pipefail

# --- Detect python runner ----------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  PYBIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYBIN="python"
else
  echo "❌ Python introuvable (python3/python)." >&2
  exit 1
fi

MANAGE="${PYBIN} manage.py"

# --- Check gettext (msgfmt) for compilemessages ------------------------------
if ! command -v msgfmt >/dev/null 2>&1; then
  echo "⚠️  'msgfmt' (gettext) est introuvable. 'compilemessages' risque d'échouer."
  echo "   Installez-le (ex: sudo apt-get install -y gettext) puis relancez."
fi

# --- Languages ---------------------------------------------------------------
# Django attend un dossier 'zh_Hans' pour le chinois simplifié
DEFAULT_LANGS=(fr en es wo de it pt ar nb sv fi da nl pl ru zh_Hans ja)

# Priorité aux arguments, puis à $LANGS, sinon liste par défaut.
if [[ $# -gt 0 ]]; then
  LANGS=("$@")
elif [[ -n "${LANGS:-}" ]]; then
  # shellcheck disable=SC2206
  LANGS=(${LANGS})
else
  LANGS=("${DEFAULT_LANGS[@]}")
fi

# --- Ignores (ajoutez les vôtres si besoin) ---------------------------------
IGNORES=(venv node_modules "static/*" "media/*" "**/*.min.js" ".git" ".tox" "__pycache__")

ignore_args=()
for p in "${IGNORES[@]}"; do
  ignore_args+=(--ignore "$p")
done

# --- Ensure locale directory exists -----------------------------------------
mkdir -p locale

echo "==> Langues cibles: ${LANGS[*]}"
echo "==> Génération des .po (domaine 'django' : .py/.html/.txt)"
for L in "${LANGS[@]}"; do
  ${MANAGE} makemessages -l "$L" "${ignore_args[@]}" --extension=py,html,txt
done

echo "==> Génération des .po (domaine 'djangojs' : .js/.jsx/.ts/.tsx)"
for L in "${LANGS[@]}"; do
  ${MANAGE} makemessages -d djangojs -l "$L" "${ignore_args[@]}" --extension=js,jsx,ts,tsx
done

echo "==> Compilation des messages (.mo)"
${MANAGE} compilemessages

echo "✅ Terminé. Fichiers créés/maj dans locale/<lang>/LC_MESSAGES/ (django.po, djangojs.po)."
