#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
# Explicitly install gunicorn in the system path for Render
pip install gunicorn
pip install -r requirements.txt


python manage.py migrate --noinput

# TEMP: Create admin user if missing on next deploy
python manage.py create_admin_user

# TEMP: Import restaurants and assign to admin on next deploy
python add_restaurants.py

# Load restaurant data if none exist
if python manage.py shell -c "from restaurants.models import Restaurant; exit(0 if Restaurant.objects.count() == 0 else 1)"; then
	echo "Loading initial restaurant data..."
	python load_restaurants.py
else
	echo "⚠️ Data already exists, skipping restaurant data load"
fi


python manage.py collectstatic --noinput
