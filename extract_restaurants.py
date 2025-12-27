import os
import django
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from restaurants.models import Restaurant

# Extract all restaurants from local DB
restaurants = []
for r in Restaurant.objects.all():
    restaurants.append({
        "name": r.name,
        "description": r.description,
        "address": r.address,
        "phone": r.phone,
        "email": r.email,
        "is_active": r.is_active,
    })

with open("local_restaurants_data.json", "w", encoding="utf-8") as f:
    json.dump(restaurants, f, indent=2, ensure_ascii=False)

print(f"Exported {len(restaurants)} restaurants to local_restaurants_data.json")
