#!/usr/bin/env bash
set -o errexit

# Install system dependencies for GDAL
apt-get update
apt-get install -y libgdal-dev gdal-bin binutils libproj-dev proj-data proj-bin

# Install Python dependencies
pip install -r requirements.txt

# Configure GDAL environment
export GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
export GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations with PostGIS
python manage.py migrate

# Create PostGIS extension if not exists
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    try:
        cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
        print('PostGIS extension created successfully')
    except Exception as e:
        print(f'Error creating PostGIS extension: {e}')
"