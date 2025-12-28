import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from django.test import Client
from restaurants.models import Restaurant

User = get_user_model()

username = 'tmp_owner'
password = 'tmp_password'
user, created = User.objects.get_or_create(username=username, defaults={'email':'tmp@example.com'})
if created:
    user.set_password(password)
    user.role = 'restaurant_owner'
    user.save()
else:
    user.role = 'restaurant_owner'
    user.set_password(password)
    user.save()

# ensure there is no extra restaurants for clarity
Restaurant.objects.filter(owner=user).delete()

# create one restaurant for the owner
rest, _ = Restaurant.objects.get_or_create(name='Temp Rest', owner=user, defaults={'slug':'temp-rest','description':'test','opening_time':'09:00:00','closing_time':'21:00:00','is_active':True})

c = Client()
logged = c.login(username=username, password=password)
print('logged in:', logged)
resp = c.get('/restaurants/dashboard/')
print('status_code:', resp.status_code)
content = resp.content.decode('utf-8')
# print lines that contain Add Restaurant or Add Your First
for i, line in enumerate(content.splitlines()):
    if 'Add Restaurant' in line or 'Add Your' in line or 'manage_restaurant' in line or "fa-plus" in line:
        print(i+1, line.strip())

# Save full content for review
with open('tmp_owner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved tmp_owner_dashboard.html')
