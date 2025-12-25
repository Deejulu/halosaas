#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
# Explicitly install gunicorn in the system path for Render
pip install gunicorn
pip install -r requirements.txt


python manage.py migrate --noinput

# Load restaurant data if none exist
if python manage.py shell -c "from restaurants.models import Restaurant; exit(0 if Restaurant.objects.count() == 0 else 1)"; then
	echo "Loading initial restaurant data..."
	python load_data.py
else
	echo "⚠️ Data already exists, skipping restaurant data load"
fi

# Create admin user if not exists using script
echo "Checking/Creating admin user..."
python create_admin.py

python manage.py collectstatic --noinput
