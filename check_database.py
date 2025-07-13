from django.db import connections
from django.db.utils import OperationalError

try:
    db_conn = connections['default']
    db_conn.cursor()
    print("✅ Connexion à la base de données OK.")
except OperationalError as e:
    print(f"❌ Échec de connexion à la base de données : {e}")
