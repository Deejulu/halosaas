from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, MenuItem, Category

SAMPLE_MENUS = {
    'Naija Grill House': [
        {'name': 'Lagos Suya Platter', 'description': 'Spicy beef, chicken, and ram suya, served with onions and yaji. A Lagos street classic.', 'price': 4000},
        {'name': 'Grilled Catfish', 'description': 'Whole catfish grilled with secret spices, served with pepper sauce.', 'price': 5000},
        {'name': 'Jollof Fiesta', 'description': 'Party-style jollof rice, fried plantain, and grilled turkey.', 'price': 3500},
        {'name': 'Palmwine', 'description': 'Chilled, fresh palmwine from Ogun State.', 'price': 1200},
    ],
    'Bukka Republic': [
        {'name': 'Efo Riro Supreme', 'description': 'Spinach stew with assorted meats, ponmo, and stockfish. Ibadan’s favorite.', 'price': 3500},
        {'name': 'Amala Gbegiri Combo', 'description': 'Soft amala, ewedu, gbegiri, and spicy goat meat.', 'price': 3200},
        {'name': 'Ofada Rice & Ayamase', 'description': 'Local rice with green pepper sauce and fried beef.', 'price': 3800},
        {'name': 'Zobo Drink', 'description': 'Refreshing hibiscus drink with pineapple and ginger.', 'price': 900},
    ],
    'Jollof City': [
        {'name': 'Smoky Jollof Rice', 'description': 'Enugu-style jollof with grilled chicken and spicy sauce.', 'price': 3400},
        {'name': 'Moi Moi Deluxe', 'description': 'Bean pudding with egg, fish, and corned beef.', 'price': 1800},
        {'name': 'Fried Croaker', 'description': 'Crispy fried croaker fish, pepper sauce, and yam fries.', 'price': 4200},
        {'name': 'Chapman', 'description': 'Classic Nigerian cocktail with bitters and citrus.', 'price': 1500},
    ],
    'Palmwine Place': [
        {'name': 'Isi Ewu', 'description': 'Tender goat head in spicy palm oil sauce, garnished Igbo-style.', 'price': 5000},
        {'name': 'Nkwobi', 'description': 'Cow foot in spicy sauce, served with utazi leaves.', 'price': 4200},
        {'name': 'Ukodo', 'description': 'Delta yam pepper soup with goat meat.', 'price': 3500},
        {'name': 'Palmwine Jug', 'description': 'Large jug of fresh palmwine, perfect for sharing.', 'price': 2500},
    ],
    'Pepper Soup Spot': [
        {'name': 'Catfish Pepper Soup', 'description': 'Port Harcourt-style spicy catfish soup with scent leaves.', 'price': 3700},
        {'name': 'Chicken Pepper Soup', 'description': 'Tender chicken in hot, aromatic broth.', 'price': 3400},
        {'name': 'Yam Porridge', 'description': 'Yam cooked with palm oil, vegetables, and smoked fish.', 'price': 2800},
        {'name': 'Palm Toddy', 'description': 'Sweet, chilled palm toddy drink.', 'price': 1000},
    ],
    'Chop Life Lounge': [
        {'name': 'Asun Deluxe', 'description': 'Peppery grilled goat meat, onions, and bell peppers. Abuja’s party favorite.', 'price': 4800},
        {'name': 'Grilled Prawns', 'description': 'Charcoal grilled prawns with spicy pepper dip.', 'price': 6000},
        {'name': 'Peppered Snails', 'description': 'Large snails sautéed in hot pepper sauce.', 'price': 5500},
        {'name': 'Tigernut Punch', 'description': 'Creamy, sweet tigernut and coconut drink.', 'price': 1200},
    ],
    'Ofada Kitchen': [
        {'name': 'Ofada Rice & Designer Stew', 'description': 'Abeokuta’s finest: local rice, spicy assorted meat stew.', 'price': 4000},
        {'name': 'Stewed Snails', 'description': 'Snails in rich tomato and pepper sauce.', 'price': 5000},
        {'name': 'Fried Dodo', 'description': 'Golden fried plantain, sweet and crispy.', 'price': 1500},
        {'name': 'Kunu Drink', 'description': 'Northern Nigerian millet drink, served cold.', 'price': 1000},
    ],
    # Add more restaurants and unique menus as needed
}

class Command(BaseCommand):
    help = 'Populate beautiful sample menu items for each restaurant.'

    def handle(self, *args, **options):
        for restaurant in Restaurant.objects.all():
            # Ensure a default category exists
            category, _ = Category.objects.get_or_create(
                restaurant=restaurant,
                name="Main Dishes",
                defaults={"description": "Signature and popular dishes."}
            )
            menu = SAMPLE_MENUS.get(restaurant.name)
            if not menu:
                menu = [
                    {'name': 'Chef Special', 'description': 'Signature dish of the house.', 'price': 3000},
                    {'name': 'Classic Rice', 'description': 'Rice with sauce and protein.', 'price': 2500},
                    {'name': 'Fresh Juice', 'description': 'Seasonal fruit juice.', 'price': 1000},
                ]
            for item in menu:
                MenuItem.objects.get_or_create(
                    category=category,
                    name=item['name'],
                    defaults={
                        'description': item['description'],
                        'price': item['price'],
                        'is_available': True,
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"✅ Menu created for {restaurant.name}"))
        self.stdout.write(self.style.SUCCESS("All sample menus created!"))
