import os
import django

# Set up Django to use your live Render database
os.environ['DATABASE_URL'] = 'postgresql://halosaas_user:YsPEvL7nMQxefH2u1F0bpNr8cEM1B9OA@dpg-d56g8tchg0os73am2gng-a.oregon-postgres.render.com:5432/halosaas'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')

django.setup()

from restaurants.models import Restaurant
from django.contrib.auth import get_user_model

User = get_user_model()


# Get your admin user (username='halosaasadmin')
try:
    owner = User.objects.get(username='halosaasadmin')
except User.DoesNotExist:
    print("Admin user 'halosaasadmin' does not exist. Please create it first.")
    exit(1)


# Load restaurant data from local_restaurants_data.json
import json
with open("local_restaurants_data.json", "r", encoding="utf-8") as f:
    restaurants = json.load(f)




created = 0
from django.db import IntegrityError

for data in restaurants:
    data['owner'] = owner
    data['is_active'] = True
    # Set default opening and closing times if missing
    if 'opening_time' not in data or not data['opening_time']:
        data['opening_time'] = '09:00:00'
    if 'closing_time' not in data or not data['closing_time']:
        data['closing_time'] = '22:00:00'
    # Add required fields if missing
    if 'slug' not in data or not data['slug']:
        data['slug'] = data['name'].lower().replace(' ', '-')
    if 'logo' not in data:
        data['logo'] = None
    if 'banner_image' not in data:
        data['banner_image'] = None
    try:
        # Try to update existing restaurant by slug
        restaurant, created_flag = Restaurant.objects.update_or_create(
            slug=data['slug'],
            defaults=data
        )
        if created_flag:
            print(f"  ✅ Created: {restaurant.name}")
        else:
            print(f"  🔄 Updated: {restaurant.name}")
        created += 1
    except IntegrityError as e:
        print(f"❌ Failed to create/update {data.get('name', '[no name]')}: {e}")
        print(f"Data: {data}")


print(f"\n🎉 Created {created} restaurants, all owned by {owner.username}")
print("💡 Restaurants should now appear on your live site!")
