from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, Category, MenuItem

class Command(BaseCommand):
    help = "Add an 'Award Class' menu with diverse categories and items to every restaurant."

    def handle(self, *args, **options):
        sample_categories = [
            {
                'name': 'Award Starters',
                'description': 'Award-winning appetizers to begin your meal',
                'items': [
                    {'name': 'Golden Calamari', 'description': 'Crispy calamari rings with aioli', 'price': 2200},
                    {'name': 'Signature Spring Rolls', 'description': 'Vegetable spring rolls with sweet chili dip', 'price': 1500},
                ]
            },
            {
                'name': 'Award Mains',
                'description': 'Main courses recognized for excellence',
                'items': [
                    {'name': 'Chef’s Special Jollof', 'description': 'Award-winning jollof rice with grilled chicken', 'price': 3500},
                    {'name': 'Seafood Supreme', 'description': 'Grilled fish and prawns with lemon butter', 'price': 4800},
                ]
            },
            {
                'name': 'Award Desserts',
                'description': 'Desserts that have won hearts and awards',
                'items': [
                    {'name': 'Chocolate Dream', 'description': 'Rich chocolate cake with molten center', 'price': 1800},
                    {'name': 'Tropical Fruit Parfait', 'description': 'Layers of fresh fruit, yogurt, and granola', 'price': 1300},
                ]
            },
            {
                'name': 'Award Drinks',
                'description': 'Beverages with a special touch',
                'items': [
                    {'name': 'Classic Chapman', 'description': 'Nigerian fruity cocktail', 'price': 1000},
                    {'name': 'Zobo Royale', 'description': 'Hibiscus drink with a twist', 'price': 900},
                ]
            },
        ]

        restaurants = Restaurant.objects.all()
        for restaurant in restaurants:
            self.stdout.write(f"Adding Award Class menu to {restaurant.name}...")
            for cat_data in sample_categories:
                category, created = Category.objects.get_or_create(
                    restaurant=restaurant,
                    name=cat_data['name'],
                    defaults={'description': cat_data['description']}
                )
                for item in cat_data['items']:
                    MenuItem.objects.get_or_create(
                        category=category,
                        name=item['name'],
                        defaults={
                            'description': item['description'],
                            'price': item['price'],
                            'is_available': True
                        }
                    )
            self.stdout.write(self.style.SUCCESS(f"Award Class menu added to {restaurant.name}."))
        self.stdout.write(self.style.SUCCESS('Award Class menu setup complete for all restaurants.'))
