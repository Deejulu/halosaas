import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from django.core.management import call_command

call_command('loaddata', 'restaurants.json')
print("✅ Restaurants loaded")
