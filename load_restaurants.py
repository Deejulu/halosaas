# This script loads the restaurants.json fixture automatically if not already loaded.
import os
import django
from django.core.management import call_command
from django.db.utils import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from restaurants.models import Restaurant

fixture_file = os.path.join(os.path.dirname(__file__), 'restaurants.json')

try:
    print('Deleting all existing restaurants...')
    Restaurant.objects.all().delete()
    print('Loading fixture...')
    call_command('loaddata', fixture_file)
    print('Fixture loaded successfully.')
except IntegrityError as e:
    print(f'IntegrityError: {e}')
except Exception as e:
    print(f'Error loading fixture: {e}')
