import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from django.core.management import call_command
from restaurants.models import Restaurant

def check_json_encoding(file_path):
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			json.load(f)
		return True
	except UnicodeDecodeError:
		print(f"❌ {file_path} has wrong encoding (not UTF-8)")
		return False
	except json.JSONDecodeError as e:
		print(f"❌ Invalid JSON in {file_path}: {e}")
		return False

if Restaurant.objects.count() == 0:
	print("Loading initial restaurant data...")
	fixture_file = 'restaurants.json'
	if not check_json_encoding(fixture_file):
		print("⚠️ Skipping data load due to encoding issues")
		sys.exit(0)
	try:
		call_command('loaddata', fixture_file)
		print(f"✅ Successfully loaded {Restaurant.objects.count()} restaurants")
	except Exception as e:
		print(f"❌ Error loading restaurants: {e}")
		print("⚠️ Continuing without restaurant data")
else:
	print(f"⚠️ {Restaurant.objects.count()} restaurants already exist, skipping data load")
