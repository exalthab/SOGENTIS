#!/bin/bash
set -e

###############################################################################
# SOGENTIS - INSTALLATION STEP 7 : Configuration Dashboard Django pro
# Adapté au projet Django existant avec app dashboard
###############################################################################

PROJECT_NAME="SOGENTIS"
PROJECT_DIR="$HOME/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_MANAGE="$PROJECT_DIR/manage.py"
ADMIN_EMAIL="admin@sogentis.org"  # Modifie selon ton besoin

echo -e "\n==============================="
echo " SOGENTIS - INSTALLATION STEP 7 : Dashboard Django pro"
echo "===============================\n"

# Vérifier existence projet Django et venv
if [ ! -f "$DJANGO_MANAGE" ]; then
    echo "Erreur : manage.py introuvable dans $PROJECT_DIR"
    exit 1
fi
if [ ! -d "$VENV_DIR" ]; then
    echo "Erreur : environnement virtuel introuvable dans $VENV_DIR"
    exit 1
fi

# Activer l'environnement virtuel
source "$VENV_DIR/bin/activate"

# Installer dépendances pour dashboard
echo "[1] Installation dépendances Python nécessaires..."
pip install django-bootstrap4 django-widget-tweaks psutil

# Modifier settings.py pour inclure 'dashboard', 'bootstrap4', 'widget_tweaks'
SETTINGS_FILE="$PROJECT_DIR/config/settings.py"
if ! grep -q "'dashboard'" "$SETTINGS_FILE"; then
    echo "[2] Ajout des apps dashboard et bootstrap4 dans settings.py"
    sed -i "/INSTALLED_APPS = \[/a \    'dashboard',\n    'bootstrap4',\n    'widget_tweaks'," "$SETTINGS_FILE"
else
    echo "Apps dashboard et bootstrap4 déjà présentes dans settings.py"
fi

# Modifier settings.py pour forcer login sur dashboard (middleware)
if ! grep -q "LoginRequiredMiddleware" "$SETTINGS_FILE"; then
    echo "[3] Ajout middleware LoginRequiredMiddleware dans settings.py"
    sed -i "/MIDDLEWARE = \[/a \    'django.contrib.auth.middleware.AuthenticationMiddleware',\n    'django.contrib.messages.middleware.MessageMiddleware',\n    'django.contrib.sessions.middleware.SessionMiddleware',\n    'dashboard.middleware.LoginRequiredMiddleware'," "$SETTINGS_FILE"
fi

# Créer middleware LoginRequiredMiddleware dans dashboard/middleware.py si pas existant
MIDDLEWARE_FILE="$PROJECT_DIR/dashboard/middleware.py"
if [ ! -f "$MIDDLEWARE_FILE" ]; then
    echo "[4] Création middleware LoginRequiredMiddleware"
    cat > "$MIDDLEWARE_FILE" <<EOF
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith(reverse('login')):
            return redirect('login')
        return self.get_response(request)
EOF
else
    echo "Middleware LoginRequiredMiddleware déjà présent."
fi

# Créer vues basiques dashboard/views.py (état services, CPU/mem, backup)
VIEWS_FILE="$PROJECT_DIR/dashboard/views.py"
echo "[5] Création ou mise à jour dashboard/views.py"
cat > "$VIEWS_FILE" <<'EOF'
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import subprocess
import psutil
import os

@login_required
def home(request):
    # Afficher stats CPU/mem
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    memory_percent = mem.percent

    # Vérifier statut services (gunicorn, nginx, postgresql, redis)
    services = ['gunicorn', 'nginx', 'postgresql', 'redis-server']
    statuses = {}
    for service in services:
        result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
        statuses[service] = result.stdout.strip()

    context = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'statuses': statuses,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def backup(request):
    # Appeler scripts backup base et media (modifie si chemin différent)
    BASE_DIR = os.path.expanduser('~/SOGENTIS')
    backup_db_script = os.path.join(BASE_DIR, 'backup_db.sh')
    backup_media_script = os.path.join(BASE_DIR, 'backup_media.sh')

    db_result = subprocess.run(['bash', backup_db_script])
    media_result = subprocess.run(['bash', backup_media_script])

    messages = []
    if db_result.returncode == 0:
        messages.append('Backup base de données réussi.')
    else:
        messages.append('Backup base de données échoué.')

    if media_result.returncode == 0:
        messages.append('Backup média réussi.')
    else:
        messages.append('Backup média échoué.')

    return render(request, 'dashboard/backup.html', {'messages': messages})

@login_required
def logs(request):
    LOG_FILE = os.path.expanduser('~/SOGENTIS/logs/django.log')
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()[-100:]  # Dernières 100 lignes
    return render(request, 'dashboard/logs.html', {'logs': logs})
EOF

# Créer urls.py dans dashboard si pas existant
URLS_FILE="$PROJECT_DIR/dashboard/urls.py"
if [ ! -f "$URLS_FILE" ]; then
    echo "[6] Création dashboard/urls.py"
    cat > "$URLS_FILE" <<'EOF'
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    path('backup/', views.backup, name='dashboard_backup'),
    path('logs/', views.logs, name='dashboard_logs'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
EOF
else
    echo "dashboard/urls.py déjà existant"
fi

# Modifier urls.py principal pour inclure dashboard.urls
MAIN_URLS_FILE="$PROJECT_DIR/config/urls.py"
if ! grep -q "dashboard.urls" "$MAIN_URLS_FILE"; then
    echo "[7] Inclusion des URLs dashboard dans config/urls.py"
    sed -i "/from django.urls import path, include/a from django.urls import include" "$MAIN_URLS_FILE"
    sed -i "/urlpatterns = \[/a \    path('', include('dashboard.urls'))," "$MAIN_URLS_FILE"
else
    echo "dashboard.urls déjà inclus dans config/urls.py"
fi

# Créer templates dashboard minimalistes avec Bootstrap
TEMPLATES_DIR="$PROJECT_DIR/dashboard/templates/dashboard"
mkdir -p "$TEMPLATES_DIR"

echo "[8] Création templates minimalistes avec Bootstrap"

# base.html
cat > "$TEMPLATES_DIR/base.html" <<'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="{% url 'dashboard_home' %}">SOGENTIS Dashboard</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item"><a class="nav-link" href="{% url 'dashboard_home' %}">Accueil</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'dashboard_backup' %}">Backups</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'dashboard_logs' %}">Logs</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'logout' %}">Déconnexion</a></li>
      </ul>
    </div>
  </div>
</nav>
<div class="container">
    {% block content %}
    {% endblock %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

# home.html
cat > "$TEMPLATES_DIR/home.html" <<'EOF'
{% extends "dashboard/base.html" %}
{% block title %}Accueil{% endblock %}
{% block content %}
<h1>Bienvenue sur le Dashboard SOGENTIS</h1>
<p>Utilisation CPU: {{ cpu_percent }}%</p>
<p>Utilisation Mémoire: {{ memory_percent }}%</p>

<h3>Statut des services :</h3>
<ul>
  {% for service, status in statuses.items %}
    <li><strong>{{ service }}</strong> : 
        {% if status == "active" %}
            <span class="text-success">Actif</span>
        {% else %}
            <span class="text-danger">Inactif</span>
        {% endif %}
    </li>
  {% endfor %}
</ul>
{% endblock %}
EOF

# backup.html
cat > "$TEMPLATES_DIR/backup.html" <<'EOF'
{% extends "dashboard/base.html" %}
{% block title %}Backups{% endblock %}
{% block content %}
<h1>Backups</h1>
<ul>
  {% for message in messages %}
    <li>{{ message }}</li>
  {% endfor %}
</ul>
<a href="{% url 'dashboard_home' %}" class="btn btn-primary">Retour</a>
{% endblock %}
EOF

# logs.html
cat > "$TEMPLATES_DIR/logs.html" <<'EOF'
{% extends "dashboard/base.html" %}
{% block title %}Logs{% endblock %}
{% block content %}
<h1>Logs Django (dernières 100 lignes)</h1>
<pre style="background:#f8f9fa; padding:15px; border:1px solid #ddd;">
{% for line in logs %}
{{ line }}
{% endfor %}
</pre>
<a href="{% url 'dashboard_home' %}" class="btn btn-primary">Retour</a>
{% endblock %}
EOF

# login.html
cat > "$TEMPLATES_DIR/login.html" <<'EOF'
{% extends "dashboard/base.html" %}
{% block title %}Connexion{% endblock %}
{% block content %}
<h2>Connexion</h2>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">Se connecter</button>
</form>
{% endblock %}
EOF

# Migrer la base de données (au cas où dashboard a des modèles)
echo "[9] Migration base de données Django"
python "$DJANGO_MANAGE" migrate

# Créer superuser interactif
echo "[10] Création d'un superutilisateur Django"
python "$DJANGO_MANAGE" createsuperuser

echo
echo "==================================="
echo " Dashboard Django configuré et prêt !"
echo " Accède à : http://ton_domaine_ou_ip/"
echo " Connecte-toi avec ton superuser"
echo " Personnalise les templates, ajoute tes vues et métriques"
echo "==================================="

deactivate
exit 0
