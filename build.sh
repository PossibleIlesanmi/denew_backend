#!/usr/bin/env bash
# build.sh for Render deployment
set -o errexit  # exit on error

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Create migrations and migrate
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create superuser if environment variables are set (idempotent if already exists)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --noinput || true
fi