#!/bin/bash
# Ce script télécharge Chart.js, Chartjs-Chart-Geo, et le fichier monde json dans static/dashboard/chartjs/

set -e

STATIC_DIR="sogentis_apps/dashboard/static/dashboard/chartjs"
mkdir -p $STATIC_DIR

echo "Téléchargement de Chart.js..."
curl -L -o $STATIC_DIR/chart.min.js "https://cdn.jsdelivr.net/npm/chart.js"

echo "Téléchargement de Chartjs-Chart-Geo (fichier build minifié)..."
curl -L -o $STATIC_DIR/chartjs-chart-geo.min.js "https://cdn.jsdelivr.net/npm/chartjs-chart-geo@4.3.3/build/chartjs-chart-geo.min.js"

echo "Téléchargement du fichier GeoJSON du monde (countries-110m.json)..."
curl -L -o $STATIC_DIR/countries-110m.json "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

echo "Tous les fichiers nécessaires ont été téléchargés dans $STATIC_DIR"
ls -lh $STATIC_DIR
