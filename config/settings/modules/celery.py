from decouple import config

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/1")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Optionnel, tu peux aussi ajouter plus de configs Celery ici
