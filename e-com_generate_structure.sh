#!/bin/bash

# ROOT="/c/A/B/C/D/E/SOGENTIS/sogentis_apps/economic"
ROOT="C:/Users/HP/Documents/sogentis_docs/infomaniak/SOGENTIS/sogentis_apps/economic"

# ====================================================
# Fonctions sécurisées
# ====================================================

safe_touch() {
    if [ -f "$1" ]; then
        echo "⚠️  Fichier existe déjà, ignoré : $1"
    else
        mkdir -p "$(dirname "$1")"
        touch "$1"
        echo "✔️  Fichier créé : $1"
    fi
}

safe_mkdir() {
    if [ -d "$1" ]; then
        echo "⚠️  Dossier existe déjà, ignoré : $1"
    else
        mkdir -p "$1"
        echo "✔️  Dossier créé : $1"
    fi
}

echo "===================================================="
echo "   CRÉATION SÉCURISÉE DU PÔLE ÉCONOMIQUE DJANGO"
echo "===================================================="
echo "Chemin : $ROOT"
echo

# ====================================================
# APP ECONOMIC ROOT
# ====================================================

safe_mkdir "$ROOT"

for f in __init__.py apps.py urls.py permissions.py context_processors.py
do
    safe_touch "$ROOT/$f"
done

# ====================================================
# ECOMMERCE
# ====================================================

EC="$ROOT/ecommerce"
safe_mkdir "$EC"

for d in models admin views services templates/ecommerce/orders static/ecommerce/css static/ecommerce/js
do
    safe_mkdir "$EC/$d"
done

for m in category product product_image review cart cart_item order order_item wishlist vendor
do
    safe_touch "$EC/models/$m.py"
done
safe_touch "$EC/models/__init__.py"

for a in category_admin product_admin order_admin vendor_admin
do
    safe_touch "$EC/admin/$a.py"
done
safe_touch "$EC/admin/__init__.py"

for v in catalog product_detail cart checkout orders wishlist
do
    safe_touch "$EC/views/$v.py"
done
safe_touch "$EC/views/__init__.py"

for s in pricing_service cart_service order_service stock_service
do
    safe_touch "$EC/services/$s.py"
done
safe_touch "$EC/services/__init__.py"

for t in catalog product_detail cart checkout
do
    safe_touch "$EC/templates/ecommerce/$t.html"
done

safe_touch "$EC/templates/ecommerce/orders/order_list.html"
safe_touch "$EC/templates/ecommerce/orders/order_detail.html"

safe_touch "$EC/apps.py"
safe_touch "$EC/urls.py"
safe_touch "$EC/permissions.py"

# ====================================================
# FORMATIONS
# ====================================================

FORM="$ROOT/formations"
safe_mkdir "$FORM"

safe_mkdir "$FORM/models"
safe_mkdir "$FORM/views"
safe_mkdir "$FORM/services"
safe_mkdir "$FORM/templates/formations"
safe_mkdir "$FORM/static/formations/css"
safe_mkdir "$FORM/static/formations/js"
safe_mkdir "$FORM/admin"

safe_touch "$FORM/__init__.py"
safe_touch "$FORM/apps.py"
safe_touch "$FORM/urls.py"
safe_touch "$FORM/views/__init__.py"
safe_touch "$FORM/admin/__init__.py"

for m in course module lesson enrollment certificate
do
    safe_touch "$FORM/models/$m.py"
done
safe_touch "$FORM/models/__init__.py"

for v in catalog course_detail learning certificates
do
    safe_touch "$FORM/views/$v.py"
done

safe_touch "$FORM/services/enrollment_service.py"
safe_touch "$FORM/services/certificate_service.py"

safe_touch "$FORM/templates/formations/catalog.html"
safe_touch "$FORM/templates/formations/course_detail.html"
safe_touch "$FORM/templates/formations/learning.html"

# ====================================================
# SERVICES NUMÉRIQUES
# ====================================================

SVC="$ROOT/services"
safe_mkdir "$SVC"

safe_mkdir "$SVC/models"
safe_mkdir "$SVC/views"
safe_mkdir "$SVC/services"
safe_mkdir "$SVC/templates/services"
safe_mkdir "$SVC/static/services/css"
safe_mkdir "$SVC/static/services/js"
safe_mkdir "$SVC/admin"

safe_touch "$SVC/__init__.py"
safe_touch "$SVC/apps.py"
safe_touch "$SVC/urls.py"
safe_touch "$SVC/views/__init__.py"
safe_touch "$SVC/admin/__init__.py"

for m in service service_category quote maintenance_ticket
do
    safe_touch "$SVC/models/$m.py"
done
safe_touch "$SVC/models/__init__.py"

for v in services_list service_detail request_quote tickets
do
    safe_touch "$SVC/views/$v.py"
done

safe_touch "$SVC/services/quote_service.py"
safe_touch "$SVC/services/ticket_service.py"

safe_touch "$SVC/templates/services/services_list.html"
safe_touch "$SVC/templates/services/service_detail.html"
safe_touch "$SVC/templates/services/quote_form.html"

# ====================================================
# B2B
# ====================================================

B2B="$ROOT/b2b"
safe_mkdir "$B2B"

safe_mkdir "$B2B/models"
safe_mkdir "$B2B/views"
safe_mkdir "$B2B/services"
safe_mkdir "$B2B/templates/b2b"
safe_mkdir "$B2B/static/b2b/css"
safe_mkdir "$B2B/static/b2b/js"
safe_mkdir "$B2B/admin"

safe_touch "$B2B/__init__.py"
safe_touch "$B2B/apps.py"
safe_touch "$B2B/urls.py"
safe_touch "$B2B/permissions.py"
safe_touch "$B2B/views/__init__.py"
safe_touch "$B2B/admin/__init__.py"

for m in company company_user bulk_order invoice
do
    safe_touch "$B2B/models/$m.py"
done
safe_touch "$B2B/models/__init__.py"

for v in dashboard bulk_orders invoices vendors
do
    safe_touch "$B2B/views/$v.py"
done

safe_touch "$B2B/services/bulk_order_service.py"
safe_touch "$B2B/services/invoice_service.py"

safe_touch "$B2B/templates/b2b/dashboard.html"
safe_touch "$B2B/templates/b2b/bulk_orders.html"
safe_touch "$B2B/templates/b2b/invoices.html"

# ====================================================
# RESOURCES
# ====================================================

RES="$ROOT/resources"
safe_mkdir "$RES"

safe_mkdir "$RES/models"
safe_mkdir "$RES/templates/resources"
safe_mkdir "$RES/admin"

safe_touch "$RES/__init__.py"
safe_touch "$RES/apps.py"
safe_touch "$RES/urls.py"
safe_touch "$RES/views.py"
safe_touch "$RES/models/resource.py"
safe_touch "$RES/models/__init__.py"
safe_touch "$RES/admin/__init__.py"
safe_touch "$RES/templates/resources/resources_list.html"

# ====================================================
# SUPPORT
# ====================================================

SUP="$ROOT/support"
safe_mkdir "$SUP"

safe_mkdir "$SUP/models"
safe_mkdir "$SUP/templates/support"
safe_mkdir "$SUP/admin"

safe_touch "$SUP/__init__.py"
safe_touch "$SUP/apps.py"
safe_touch "$SUP/urls.py"
safe_touch "$SUP/views.py"
safe_touch "$SUP/models/support_ticket.py"
safe_touch "$SUP/models/__init__.py"
safe_touch "$SUP/admin/__init__.py"
safe_touch "$SUP/templates/support/faq.html"
safe_touch "$SUP/templates/support/tickets.html"

echo
echo "===================================================="
echo "🎉 STRUCTURE ÉCONOMIQUE DJANGO CRÉÉE AVEC SUCCÈS"
echo "   ✔ AUCUN FICHIER ÉCRASÉ"
echo "   ✔ ADMIN READY"
echo "   ✔ MODULAIRE & SCALABLE"
echo "===================================================="
