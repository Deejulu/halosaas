import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from restaurants.models import Restaurant, MenuItem
from django.contrib.auth import get_user_model

# Sample menus for each restaurant (customize as needed)
SAMPLE_MENUS = {
    'Naija Grill House': [
        {'name': 'Suya Platter', 'description': 'Spicy grilled beef skewers served with onions and pepper sauce.', 'price': 3500},
        {'name': 'Jollof Rice', 'description': 'Classic Nigerian jollof rice with fried plantain.', 'price': 2500},
        {'name': 'Pepper Soup', 'description': 'Hot and spicy goat meat pepper soup.', 'price': 3000},
    ],
    'Bukka Republic': [
        {'name': 'Efo Riro', 'description': 'Rich spinach stew with assorted meats.', 'price': 3200},
        {'name': 'Amala & Ewedu', 'description': 'Yam flour with ewedu soup and gbegiri.', 'price': 2800},
        {'name': 'Fried Plantain', 'description': 'Sweet fried plantain slices.', 'price': 1200},
    ],
    'Jollof City': [
        {'name': 'Party Jollof', 'description': 'Smoky party jollof rice with grilled chicken.', 'price': 3500},
        {'name': 'Moi Moi', 'description': 'Steamed bean pudding.', 'price': 1500},
        {'name': 'Fried Fish', 'description': 'Crispy fried tilapia.', 'price': 3000},
    ],
    'Palmwine Place': [
        {'name': 'Palmwine', 'description': 'Freshly tapped palmwine.', 'price': 1000},
        {'name': 'Isi Ewu', 'description': 'Goat head delicacy in spicy sauce.', 'price': 4000},
        {'name': 'Nkwobi', 'description': 'Cow foot in spicy palm oil sauce.', 'price': 3500},
    ],
    'Pepper Soup Spot': [
        {'name': 'Catfish Pepper Soup', 'description': 'Spicy catfish soup with yam.', 'price': 3500},
        {'name': 'Chicken Pepper Soup', 'description': 'Tender chicken in hot pepper soup.', 'price': 3200},
        {'name': 'Yam Porridge', 'description': 'Yam cooked in spicy sauce.', 'price': 2500},
    ],
    'Chop Life Lounge': [
        {'name': 'Asun', 'description': 'Spicy grilled goat meat.', 'price': 4000},
        {'name': 'Grilled Prawns', 'description': 'Charcoal grilled prawns with pepper sauce.', 'price': 5000},
        {'name': 'Chapman', 'description': 'Classic Nigerian cocktail.', 'price': 1500},
    ],
    'Ofada Kitchen': [
        {'name': 'Ofada Rice & Ayamase', 'description': 'Local rice with spicy green pepper sauce.', 'price': 3500},
        {'name': 'Stewed Snails', 'description': 'Snails in spicy tomato sauce.', 'price': 4500},
        {'name': 'Fried Dodo', 'description': 'Crispy fried plantain.', 'price': 1200},
    ],
}

def create_sample_menus():
    for restaurant in Restaurant.objects.all():
        menu = SAMPLE_MENUS.get(restaurant.name)
        if not menu:
            # Fallback generic menu
            menu = [
                {'name': 'Chef Special', 'description': 'Signature dish of the house.', 'price': 3000},
                {'name': 'Classic Rice', 'description': 'Rice with sauce and protein.', 'price': 2500},
                {'name': 'Fresh Juice', 'description': 'Seasonal fruit juice.', 'price': 1000},
            ]
        for item in menu:
            MenuItem.objects.get_or_create(
                restaurant=restaurant,
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'price': item['price'],
                    'is_available': True,
                }
            )
        print(f"✅ Menu created for {restaurant.name}")

if __name__ == "__main__":
    create_sample_menus()
    print("All sample menus created!")
