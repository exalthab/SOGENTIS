# =====================
# BASE / ENVIRONNEMENT
# =====================
DJANGO_ENV=prod
DEBUG=False
SECRET_KEY=s1cr9t_k4y_557659400
ALLOWED_HOSTS=sogentis.org,www.sogentis.org 

# =====================
# TEST ENV (pour vérifier que .env est bien chargé)
# =====================
TEST_ENV_VAR=hello_from_prod_env

# =====================
# LOGGING
# =====================
LOG_PATH=/home/ubuntu/SOGENTIS/logs/django_error.log

# =====================
# BASE DE DONNÉES
# =====================
DATABASE_URL=postgres://sogentis:Agateka123@localhost:5432/sogentis_dbse

# =====================
# EMAIL SMTP (PROD)
# =====================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.infomaniak.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=contact@sogentis.org
EMAIL_HOST_PASSWORD=Agateka123
DEFAULT_FROM_EMAIL=contact@sogentis.org
CONTACT_EMAIL=admin@sogentis.org

# =====================
# STRIPE
# =====================
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_prod_...
DOMAIN=https://sogentis.org

# =====================
# TEMPLATES
# =====================
USE_TEMPLATE_CACHING=True


# =====================
# REDIS (optional)
# =====================
REDIS_URL=redis://localhost:6379/1

# =====================
# AWS S3 (optionnel)
# =====================
USE_S3=False


