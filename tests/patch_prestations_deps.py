from pathlib import Path
bad=[]
for p in Path(".").rglob("sogentis_apps/economic/prestations/migrations/000*.py"):
    s=p.read_text(encoding="utf-8")
    if "('services'," in s or '("services",' in s:
        bad.append(p.as_posix())
print("BAD:", len(bad))
for b in bad: print(" -", b)
raise SystemExit(1 if bad else 0)









# import os
# import sys
# import logging
# from pathlib import Path
# import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")  # <-- adapte si besoin
# django.setup()

# from django.db import connections
# from django.db.migrations.loader import MigrationLoader

# loader = MigrationLoader(connections["default"], ignore_no_migrations=False)

# # liste toutes les migrations connues pour "prestations"
# keys = sorted([k for k in loader.disk_migrations.keys() if k[0] == "prestations"])
# print("DISK MIGRATIONS prestations:", len(keys))
# for k in keys:
#     m = loader.disk_migrations[k]
#     print(" -", k, "->", m.__file__)

# # affiche la dépendance fautive depuis le graph
# node = None
# for k in keys:
#     if k[1].startswith("0004_"):
#         node = k
#         break

# print("\n0004 NODE:", node)
# if node:
#     deps = sorted(loader.graph.dependencies.get(node, []))
#     print("DEPENDENCIES OF", node, "=>", deps)






# from pathlib import Path
# import re

# ROOT = Path(".")
# needle = "('services', '000"
# hits = []

# # 1) trouver tous les fichiers de migrations "000*.py" contenant ('services', '000
# for p in ROOT.rglob("sogentis_apps/economic/prestations/migrations/000*.py"):
#     if "prestations" not in str(p).replace("\\","/"):
#         continue
#     try:
#         s = p.read_text(encoding="utf-8")
#     except Exception:
#         continue
#     if needle in s or '("services", "000' in s or "('services'," in s or '("services",' in s:
#         hits.append(p)

# print("FOUND", len(hits), "files with services deps inside prestations migrations:")
# for p in hits:
#     print(" -", p.as_posix())

# if not hits:
#     print("\nNO HITS FOUND. Then your NodeNotFound is coming from a DIFFERENT path.")
#     print("Run:  python -c \"import prestations; print(prestations.__file__)\"  (if module exists)")




# from pathlib import Path
# import re

# mig_dir = Path("sogentis_apps/economic/prestations/migrations")
# assert mig_dir.exists(), f"Missing {mig_dir}"

# # 1) Patch dependencies tuples: ('services', '000X_...') or ("services","000X_...")
# rx_dep = re.compile(r"\(\s*([\"'])services\1\s*,\s*([\"'])(000\d+_[a-zA-Z0-9_]+|000\d+_initial|000\d+)\2\s*\)")
# # 2) Patch FK/M2M targets in migration ops: to="services.Model" / to='services.Model'
# rx_to  = re.compile(r"to\s*=\s*([\"'])services\.([a-zA-Z0-9_]+)\1")

# changed = []
# for p in sorted(mig_dir.glob("0*.py")):
#     if p.name == "__init__.py":
#         continue
#     s = p.read_text(encoding="utf-8")
#     o = s
#     s = rx_dep.sub(r"('prestations', '\3')", s)
#     s = rx_to.sub(r"to='prestations.\2'", s)
#     if s != o:
#         p.write_text(s, encoding="utf-8")
#         changed.append(p.name)

# print("patched:", len(changed))
# for n in changed:
#     print(" -", n)





# from pathlib import Path
# import re

# p = Path("sogentis_apps/economic/prestations/migrations/0004_alter_service_options_alter_servicecategory_options_and_more.py")
# s = p.read_text(encoding="utf-8")

# # remplace la dépendance exacte vers services/0003_* par prestations/0003_*
# s2 = re.sub(
#     r"\(\s*['\"]services['\"]\s*,\s*['\"](0003_[a-zA-Z0-9_]+)['\"]\s*\)",
#     r"('prestations', '\1')",
#     s
# )

# if s2 == s:
#     raise SystemExit("Aucun remplacement effectué: vérifie le nom exact du fichier 0003 dans dependencies.")
# p.write_text(s2, encoding="utf-8")
# print("OK patched:", p)





# from pathlib import Path
# import re, sys

# mig_dir = Path("sogentis_apps/economic") / "prestations" / "migrations"
# if not mig_dir.exists():
#     print("Missing:", mig_dir)
#     sys.exit(1)

# files = sorted([p for p in mig_dir.glob("0004_*.py") if p.name != "__init__.py"])
# if not files:
#     print("No 0004_*.py found in", mig_dir)
#     print("Found:", [p.name for p in sorted(mig_dir.glob("0*.py"))[:20]])
#     sys.exit(1)

# # Patch all migrations: any ('services','000X_*') -> ('prestations','000X_*')
# rx_dep = re.compile(r"\(\s*['\"]services['\"]\s*,\s*['\"](000\d+_[a-zA-Z0-9_]+|000\d+_initial|000\d+)['\"]\s*\)")
# # Patch to targets: to="services.Model" -> to="prestations.Model"
# rx_to  = re.compile(r"to\s*=\s*['\"]services\.([a-zA-Z0-9_]+)['\"]")

# changed = []
# for p in sorted([q for q in mig_dir.glob("0*.py") if q.name != "__init__.py"]):
#     s = p.read_text(encoding="utf-8")
#     o = s
#     s = rx_dep.sub(r"('prestations', '\1')", s)
#     s = rx_to.sub(r"to='prestations.\1'", s)
#     if s != o:
#         p.write_text(s, encoding="utf-8")
#         changed.append(p.name)

# print("patched files:", len(changed))
# for n in changed:
#     print(" -", n)

# print("0004 target(s):")
# for p in files:
#     print(" -", p.as_posix())











# # PATCH TOTAL: remplace TOUTES les dépendances ('services','000X_...') -> ('prestations','000X_...')
# # dans economic/prestations/migrations/*.py

# from __future__ import annotations
# import pathlib
# import re

# MIG_DIR = pathlib.Path("sogentis_apps/economic/prestations/migrations")
# if not MIG_DIR.exists():
#     raise SystemExit(f"Missing: {MIG_DIR}")

# # ('services', '0002_xxx')  -> ('prestations', '0002_xxx')
# rx = re.compile(r"\(\s*['\"]services['\"]\s*,\s*['\"](000\d+_[a-zA-Z0-9_]+|000\d+_initial|000\d+)[\"\']\s*\)")

# def patch(path: pathlib.Path) -> bool:
#     s = path.read_text(encoding="utf-8")
#     out = rx.sub(r"('prestations', '\1')", s)
#     if out != s:
#         path.write_text(out, encoding="utf-8")
#         return True
#     return False

# changed = []
# for p in sorted(MIG_DIR.glob("0*.py")):
#     if p.name == "__init__.py":
#         continue
#     if patch(p):
#         changed.append(p.as_posix())

# print("patched:", len(changed))
# for p in changed:
#     print(" -", p)

