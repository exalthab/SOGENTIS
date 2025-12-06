#!/usr/bin/env python3
"""
Crée la structure locale/ pour toutes les langues du site.
- Génère locale/<lang>/LC_MESSAGES/django.po
- Crée un fichier .po minimal si inexistant
"""

from pathlib import Path
import os

# Liste officielle des langues du site
LANGS = [
    "fr",        # Français
    "en",        # Anglais
    "de",        # Allemand
    "pt",        # Portugais
    "ar",        # Arabe
    "zh_Hans",   # Chinois simplifié
    "sw",        # Swahili
    "it",        # Italien
    "nl",        # Néerlandais
    "ru",        # Russe
    "wo",        # Wolof
]

# Dossier racine des traductions
LOCALE_DIR = Path("locale")

# Contenu de base pour chaque fichier .po
PO_HEADER = """#
# Fichier de traduction Django
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: \\n"
"PO-Revision-Date: \\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"""

def create_locales():
    for lang in LANGS:
        lang_path = LOCALE_DIR / lang / "LC_MESSAGES"
        po_file = lang_path / "django.po"

        # Crée les dossiers si nécessaires
        lang_path.mkdir(parents=True, exist_ok=True)

        if not po_file.exists():
            with open(po_file, "w", encoding="utf-8") as f:
                f.write(PO_HEADER.format(lang=lang))
            print(f"✅ Créé : {po_file}")
        else:
            print(f"ℹ️  Déjà existant : {po_file}")

if __name__ == "__main__":
    create_locales()
