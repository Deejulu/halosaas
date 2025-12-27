from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, Category, MenuItem

class Command(BaseCommand):
    help = 'Create sample categories and menu items for Buca Republic if missing.'

    def handle(self, *args, **options):
        buca = Restaurant.objects.filter(name__icontains='buca republic').first()
        if not buca:
            self.stdout.write(self.style.ERROR('No restaurant named Buca Republic found.'))
            return

        # Define your sample categories and menu items here
        sample_data = [
            {
                'name': 'Starters',
                'description': 'Tasty appetizers',
                'items': [
                    {'name': 'Spring Rolls', 'description': 'Crispy vegetable spring rolls', 'price': 1500},
                    {'name': 'Chicken Suya Skewers', 'description': 'Spicy grilled chicken skewers', 'price': 2000},
                ]
            },
            {
                'name': 'Mains',
                'description': 'Delicious main courses',
                'items': [
                    {'name': 'Jollof Rice & Chicken', 'description': 'Classic jollof rice with grilled chicken', 'price': 3500},
                    {'name': 'Seafood Pasta', 'description': 'Pasta with mixed seafood in tomato sauce', 'price': 4000},
                ]
            },
            {
                'name': 'Desserts',
                'description': 'Sweet treats',
                'items': [
                    {'name': 'Chocolate Lava Cake', 'description': 'Warm chocolate cake with molten center', 'price': 1800},
                    {'name': 'Fruit Parfait', 'description': 'Layers of fruit, yogurt, and granola', 'price': 1200},
                ]
            },
            {
                'name': 'Drinks',
                'description': 'Refreshing beverages',
                'items': [
                    {'name': 'Chapman', 'description': 'Nigerian fruity cocktail', 'price': 1000},
                    {'name': 'Zobo', 'description': 'Hibiscus flower drink', 'price': 800},
                ]
            },
        ]

        for cat_data in sample_data:
            category, created = Category.objects.get_or_create(
                restaurant=buca,
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Category '{category.name}' created."))
            for item in cat_data['items']:
                menu_item, item_created = MenuItem.objects.get_or_create(
                    category=category,
                    name=item['name'],
                    defaults={
                        'description': item['description'],
                        'price': item['price'],
                        'is_available': True
                    }
                )
                if item_created:
                    self.stdout.write(self.style.SUCCESS(f"Menu item '{menu_item.name}' created in '{category.name}'."))
        self.stdout.write(self.style.SUCCESS('Sample data setup complete for Buca Republic.'))
