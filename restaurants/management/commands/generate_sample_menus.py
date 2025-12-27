from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, Category, MenuItem
import random

SAMPLE_MENUS = [
    {
        'categories': [
            {
                'name': 'Starters',
                'items': [
                    'Spring Rolls', 'Chicken Wings', 'Pepper Soup', 'Bruschetta', 'Mini Samosas',
                    'Stuffed Mushrooms', 'Garlic Bread', 'Beef Kebab', 'Shrimp Tempura', 'Avocado Salad',
                    'Spicy Meatballs', 'Vegetable Skewers'
                ]
            },
            {
                'name': 'Mains',
                'items': [
                    'Jollof Rice & Chicken', 'Grilled Fish', 'Beef Burger', 'Vegetable Pasta', 'Fried Rice Special',
                    'Chicken Alfredo', 'Goat Meat Pepper Soup', 'Seafood Platter', 'BBQ Ribs', 'Pounded Yam & Egusi',
                    'Efo Riro', 'Shawarma Plate'
                ]
            },
            {
                'name': 'Desserts',
                'items': [
                    'Chocolate Cake', 'Fruit Parfait', 'Ice Cream Sundae', 'Puff-Puff', 'Banana Split',
                    'Red Velvet Cake', 'Coconut Tart', 'Apple Pie', 'Brownie', 'Akara',
                    'Sticky Toffee Pudding', 'Lemon Cheesecake'
                ]
            },
            {
                'name': 'Drinks',
                'items': [
                    'Chapman', 'Zobo', 'Pineapple Juice', 'Coke', 'Lemonade',
                    'Smoothie', 'Fanta', 'Palm Wine', 'Malt', 'Water',
                    'Tigernut Drink', 'Orange Juice'
                ]
            },
        ]
    },
    {
        'categories': [
            {
                'name': 'Appetizers',
                'items': [
                    'Mozzarella Sticks', 'Shrimp Cocktail', 'Gizdodo', 'Yam Balls', 'Chicken Suya',
                    'Spicy Gizzard', 'Plantain Chips', 'Fish Fingers', 'Chicken Popcorn', 'Egg Rolls',
                    'Mini Meat Pie', 'Corn Soup'
                ]
            },
            {
                'name': 'Signature Dishes',
                'items': [
                    'Seafood Pasta', 'Efo Riro', 'BBQ Ribs', 'Pounded Yam & Egusi', 'Grilled Turkey',
                    'Catfish Pepper Soup', 'Fried Plantain & Beans', 'Chicken Parmesan', 'Vegetable Stir Fry', 'Asun',
                    'Fisherman Soup', 'Ofada Rice & Sauce'
                ]
            },
            {
                'name': 'Sweet Treats',
                'items': [
                    'Red Velvet Cake', 'Akara', 'Coconut Tart', 'Apple Pie', 'Brownie',
                    'Ice Cream Sandwich', 'Fruit Salad', 'Pancakes', 'Donuts', 'Caramel Flan',
                    'Mango Mousse', 'Chocolate Mousse'
                ]
            },
            {
                'name': 'Beverages',
                'items': [
                    'Smoothie', 'Fanta', 'Palm Wine', 'Malt', 'Water',
                    'Cappuccino', 'Espresso', 'Milkshake', 'Soda', 'Lemon Iced Tea',
                    'Pineapple Punch', 'Berry Blast'
                ]
            },
        ]
    },
    # Add more menu templates for more variety if needed
]

class Command(BaseCommand):
    help = "Add a unique, realistic menu to every restaurant."

    def handle(self, *args, **options):
        restaurants = Restaurant.objects.all()
        for i, restaurant in enumerate(restaurants):
            menu_template = random.choice(SAMPLE_MENUS)
            self.stdout.write(f"Adding menu to {restaurant.name}...")
            for cat_data in menu_template['categories']:
                category, _ = Category.objects.get_or_create(
                    restaurant=restaurant,
                    name=cat_data['name'],
                    defaults={'description': f"{cat_data['name']} at {restaurant.name}"}
                )
                for item_name in cat_data['items']:
                    MenuItem.objects.get_or_create(
                        category=category,
                        name=item_name,
                        defaults={
                            'description': f"{item_name} served at {restaurant.name}",
                            'price': random.randint(1000, 5000),
                            'is_available': True
                        }
                    )
            self.stdout.write(self.style.SUCCESS(f"Menu added to {restaurant.name}."))
        self.stdout.write(self.style.SUCCESS('Menus created for all restaurants.'))
