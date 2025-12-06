#!/usr/bin/env python3
"""
Pré-remplit automatiquement les fichiers .po pour toutes les langues du site SOGENTIS.

- Wolof (wo) et Swahili (sw) : traduction de base si disponible
- Autres langues : fallback msgid = msgstr
"""

import polib
from pathlib import Path

# -----------------------------------
# 1) Langues du site (doivent correspondre à settings.py)
# -----------------------------------
LANGS = [
    "fr",        # Français
    "en",        # Anglais
    "de",        # Allemand
    "pt",        # Portugais
    "ar",        # Arabe
    "zh-hans",   # Chinois simplifié
    "sw",        # Swahili
    "it",        # Italien
    "nl",        # Néerlandais
    "ru",        # Russe
    "wo",        # Wolof
]

# -----------------------------------
# 2) Chemin vers le dossier locale/
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
LOCALE_DIR = BASE_DIR / "locale"

# -----------------------------------
# 3) Traductions de base pour Wo et Sw
# -----------------------------------
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
    # Ajoute ici toutes tes traductions de base importantes pour Wo/Sw
}

# -----------------------------------
# 4) Fonction pour pré-remplir un fichier .po
# -----------------------------------
def prepopulate_po(lang_code: str):
    po_file = LOCALE_DIR / lang_code / "LC_MESSAGES" / "django.po"
    if not po_file.exists():
        print(f"⚠️  Fichier {po_file} non trouvé. Lance d'abord makemessages.")
        return

    po = polib.pofile(str(po_file))
    changed = False

    for entry in po:
        if entry.msgstr.strip():
            continue  # ne touche pas si déjà traduit

        # Wolof ou Swahili : traduction de base si disponible, sinon msgid
        if lang_code in ["wo", "sw"]:
            entry.msgstr = BASIC_TRANSLATIONS.get(entry.msgid, {}).get(lang_code, entry.msgid)
            changed = True
        else:
            # Toutes les autres langues : fallback = msgid
            entry.msgstr = entry.msgid
            changed = True

    if changed:
        po.save()
        print(f"✅ Pré-remplissage terminé pour {lang_code}")
    else:
        print(f"ℹ️  Pas de changements pour {lang_code}")


# -----------------------------------
# 5) Boucle sur toutes les langues
# -----------------------------------
if __name__ == "__main__":
    for lang in LANGS:
        prepopulate_po(lang)

    print("🎯 Tous les fichiers .po ont été pré-remplis avec succès !")
