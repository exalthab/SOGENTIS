#!/bin/bash

# === Configuration ===
DOMAIN_NAME="sogentis.org"
USER_NAME=$(whoami)
PROJECT_NAME="SOGENTIS"
PROJECT_PATH="/home/$USER_NAME/$PROJECT_NAME"
NGINX_CONFIG="/etc/nginx/sites-available/$PROJECT_NAME"

# === Création du fichier NGINX ===
echo "📄 Création du fichier NGINX avec SSL pour $DOMAIN_NAME..."

sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    # Redirection automatique vers HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    access_log /var/log/nginx/${PROJECT_NAME}.access.log;
    error_log /var/log/nginx/${PROJECT_NAME}.error.log;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $PROJECT_PATH/static/;
    }

    location /media/ {
        alias $PROJECT_PATH/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_PATH/gunicorn.sock;
    }

    proxy_read_timeout 300;
}
EOF

# === Activation de la configuration ===
echo "🔗 Activation du site NGINX..."
sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/
sudo nginx -t || { echo "❌ Erreur dans la configuration NGINX"; exit 1; }
sudo systemctl reload nginx

# === Installation de Certbot et HTTPS ===
echo "🔐 Installation de Certbot & création du certificat SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Génération du certificat
sudo certbot --nginx -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME" --non-interactive --agree-tos -m "admin@$DOMAIN_NAME"

# === Renouvellement automatique ===
echo "🕓 Configuration du renouvellement automatique SSL..."
sudo systemctl list-timers | grep certbot || sudo systemctl enable certbot.timer && sudo systemctl start certbot.timer

echo "✅ SSL et redirection HTTPS configurés pour : https://$DOMAIN_NAME"
