# 📦 Outils & Dépendances de ce projet Django

## 1. Dépendances Python/Django principales

- Django 5.2.3 — Framework web principal
- djangorestframework — API REST
- django-countries — Champs de pays
- psycopg2-binary — Accès PostgreSQL
- pillow — Images et upload
- stripe, paypalrestsdk — Paiements en ligne
- xhtml2pdf, reportlab, pypdf, svglib, pyHanko — PDF/reçus/signature
- python-decouple, python-dotenv — Variables d'environnement
- pytest, pytest-django — Tests
- factory_boy, Faker — Fixtures/tests

## 2. Outils Front-end

- Bootstrap 5, FontAwesome, Chart.js (statics ou CDN)
- Fichiers CSS/JS personnalisés dans `static/`

## 3. Outils qualité/développement

- black, isort, pylint, djlint — Qualité du code
- pre-commit — Hooks Git

## 4. Services externes

- Stripe, PayPal — Paiement
- SMTP (Mailtrap, Gmail, etc.) — Envoi d’e-mails

## 5. Variables d’environnement

- Fichier `.env` utilisé, exemple :
  - STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
  - EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
  - DEBUG, ALLOWED_HOSTS

## 6. Commandes utiles

- Installer : `pip install -r requirements.txt`
- Migrer : `python manage.py migrate`
- Tester : `pytest`
- Statics : `python manage.py collectstatic`
