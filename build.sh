#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
# Explicitly install gunicorn in the system path for Render
pip install gunicorn
pip install -r requirements.txt

python manage.py migrate --noinput

# Load superuser fixture if no users exist
echo "Checking if superuser needs to be created..."
if python manage.py shell -c "from django.contrib.auth import get_user_model; exit(0 if get_user_model().objects.count() == 0 else 1)"; then
	echo "Loading superuser fixture..."
	python manage.py loaddata superuser.json
	echo "✅ Superuser created from fixture"
else
	echo "⚠️ Users already exist, skipping superuser creation"
fi

python manage.py collectstatic --noinput
