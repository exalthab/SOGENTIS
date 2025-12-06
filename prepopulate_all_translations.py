#!/usr/bin/env python3
"""
Pré-remplit les fichiers .po pour toutes les langues du site.
- Wolof (wo) et Swahili (sw) : traductions de base
- Autres langues : fallback msgid = msgstr
"""

import polib
from pathlib import Path

# Liste des langues du site
LANGS = [
    "fr",        # Français
    "en",        # Anglais
    "de",        # Allemand
    "pt",        # Portugais
    "ar",        # Arabe
    "zh_hans",   # Chinois simplifié (nom Django standard)
    "sw",        # Swahili
    "it",        # Italien
    "nl",        # Néerlandais
    "ru",        # Russe
    "wo",        # Wolof
]

# Chemin vers le dossier locale/
LOCALE_DIR = Path("locale")

# Traductions de base pour Wo et Sw
BASIC_TRANSLATIONS = {
    "Hello": {"wo": "Nanga def", "sw": "Habari"},
    "Home": {"wo": "Kër", "sw": "Nyumbani"},
    "Submit": {"wo": "Samb", "sw": "Tuma"},
    "Cancel": {"wo": "Ñakk", "sw": "Ghairi"},
    "Login": {"wo": "Jàngal", "sw": "Ingia"},
    "Logout": {"wo": "Déggal", "sw": "Toka"},
    "Username": {"wo": "Tur yu batax", "sw": "Jina la mtumiaji"},
    "Password": {"wo": "Lekkalu", "sw": "Nenosiri"},
    "Email": {"wo": "Imel", "sw": "Barua pepe"},
}

def prepopulate_po(lang_code: str):
    po_file = LOCALE_DIR / lang_code / "LC_MESSAGES" / "django.po"
    if not po_file.exists():
        print(f"⚠️  Fichier {po_file} non trouvé. Lance d'abord makemessages.")
        return

    po = polib.pofile(str(po_file))
    changed = False

    for entry in po:
        # si déjà traduit, on ne touche pas
        if entry.msgstr.strip():
            continue

        # Wolof ou Swahili : traduction de base
        if lang_code in ["wo", "sw"] and entry.msgid in BASIC_TRANSLATIONS:
            entry.msgstr = BASIC_TRANSLATIONS[entry.msgid].get(lang_code, "")
            changed = True
        # Autres langues : fallback = msgid
        elif lang_code not in ["wo", "sw"]:
            entry.msgstr = entry.msgid
            changed = True

    if changed:
        po.save()
        print(f"✅ Pré-remplissage terminé pour {lang_code}")
    else:
        print(f"ℹ️  Pas de changements pour {lang_code}")

if __name__ == "__main__":
    for lang in LANGS:
        prepopulate_po(lang)
