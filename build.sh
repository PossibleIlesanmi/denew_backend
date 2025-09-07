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
