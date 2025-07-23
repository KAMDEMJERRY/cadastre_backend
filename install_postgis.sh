#!/bin/bash

# Vérifier si on est root
if [ "$(id -u)" -ne 0 ]; then
    echo "Ce script doit être exécuté en tant que root" >&2
    exit 1
fi

# Installer PostGIS
echo "Installation de PostGIS..."
# apt-get update
# apt-get install -y postgresql-14-postgis-3 postgresql-14-postgis-3-scripts

# Vérifier l'installation
if [ ! -f "/usr/share/postgresql/14/extension/postgis.control" ]; then
    echo "Échec de l'installation de PostGIS" >&2
    exit 1
fi

# Créer l'extension
echo "Création de l'extension PostGIS dans la base 'cadastre'..."
sudo -u postgres psql -d cadastre -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Vérifier la version
echo "Vérification de la version PostGIS..."
sudo -u postgres psql -d cadastre -c "SELECT PostGIS_version();"

echo "PostGIS a été installé avec succès!"