# TEMP: Reset admin password on next deploy
python manage.py reset_admin_password
#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
# Explicitly install gunicorn in the system path for Render
pip install gunicorn
pip install -r requirements.txt


python manage.py migrate --noinput




# Create admin user if it doesn't exist
python manage.py createadmin

# Only import restaurants using add_restaurants.py
python add_restaurants.py


python manage.py collectstatic --noinput
