#!/bin/bash
# scripts/railway_setup.sh
# This script runs once after deployment on Railway to set up the database and static files

set -e # Exit immediately if a command exits with a non-zero status

echo "========================================"
echo "    Running Railway Setup Script        "
echo "========================================"

echo "1. Applying database migrations..."
python manage.py migrate

echo "2. Setting up superuser..."
# Django's createsuperuser --noinput automatically reads from:
# DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, and DJANGO_SUPERUSER_EMAIL
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser --noinput || echo "Superuser already exists or could not be created."
else
    echo "Superuser environment variables not fully set. Skipping superuser creation."
fi

echo "3. Collecting static files..."
python manage.py collectstatic --noinput

echo "========================================"
echo "    Railway Setup Script Completed      "
echo "========================================"
