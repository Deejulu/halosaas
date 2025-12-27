import os
import django

# Set up Django to use your live Render database
os.environ['DATABASE_URL'] = 'postgresql://halosaas_user:YsPEvL7nMQxefH2u1F0bpNr8cEM1B9OA@dpg-d56g8tchg0os73am2gng-a.oregon-postgres.render.com:5432/halosaas'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')

django.setup()

from restaurants.models import Restaurant
from django.contrib.auth import get_user_model

User = get_user_model()

# Get your admin user (halosaasadmin)
try:
    owner = User.objects.get(username='halosaasadmin')
except User.DoesNotExist:
    print("Admin user 'halosaasadmin' does not exist. Please create it first.")
    exit(1)


# Load restaurant data from local_restaurants_data.json
import json
with open("local_restaurants_data.json", "r", encoding="utf-8") as f:
    restaurants = json.load(f)

# Clear existing restaurants (optional)
Restaurant.objects.all().delete()
print("Cleared existing restaurants")

for data in restaurants:
    restaurant = Restaurant(**data, owner=owner)
    restaurant.save()
    print(f"  ✅ {restaurant.name}")

print(f"\n🎉 Created {Restaurant.objects.count()} restaurants, all owned by {owner.username}")
print("💡 Restaurants should now appear on your live site!")
