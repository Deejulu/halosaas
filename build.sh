#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
# Explicitly install gunicorn in the system path for Render
pip install gunicorn
pip install -r requirements.txt

python manage.py migrate --noinput


# Create admin user if not exists using script
echo "Checking/Creating admin user..."
python create_admin.py

python manage.py collectstatic --noinput
