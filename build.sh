#!/usr/bin/env bash
# build.sh - Script de build pour Render (corrigé)
set -o errexit

echo "Setting up GDAL environment..."
# Chercher GDAL
GDAL_PATHS=(
    "/usr/lib/libgdal.so"
    "/usr/lib/x86_64-linux-gnu/libgdal.so"
    "/usr/lib/x86_64-linux-gnu/libgdal.so.32"
    "/usr/lib/x86_64-linux-gnu/libgdal.so.31"
    "/usr/lib/x86_64-linux-gnu/libgdal.so.30"
    "/usr/local/lib/libgdal.so"
)

for path in "${GDAL_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "Found GDAL at: $path"
        export GDAL_LIBRARY_PATH="$path"
        break
    fi
done

# Chercher GEOS
GEOS_PATHS=(
    "/usr/lib/libgeos_c.so"
    "/usr/lib/x86_64-linux-gnu/libgeos_c.so"
    "/usr/lib/x86_64-linux-gnu/libgeos_c.so.1"
    "/usr/local/lib/libgeos_c.so"
)

for path in "${GEOS_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "Found GEOS at: $path"
        export GEOS_LIBRARY_PATH="$path"
        break
    fi
done

export PROJ_LIB=/usr/share/proj
export RENDER=true



echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build completed successfully!"