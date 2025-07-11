# config/settings/modules/database.py

import dj_database_url
from decouple import config

DATABASE_URL = config("DATABASE_URL", default=None)
if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set!")

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

if not config("DEBUG", default=False, cast=bool):
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
