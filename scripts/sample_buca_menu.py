from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, Category, MenuItem

class Command(BaseCommand):
    help = 'Create sample categories and menu items for Buca Republic if missing.'

    def handle(self, *args, **options):
        buca = Restaurant.objects.filter(name__icontains='buca republic').first()
        if not buca:
            self.stdout.write(self.style.ERROR('No restaurant named Buca Republic found.'))
            return
        # Create sample categories if none exist
        categories = Category.objects.filter(restaurant=buca)
        if not categories.exists():
            categories = [
                Category.objects.create(restaurant=buca, name='Starters', description='Tasty appetizers'),
                Category.objects.create(restaurant=buca, name='Mains', description='Delicious main courses'),
                Category.objects.create(restaurant=buca, name='Desserts', description='Sweet treats'),
            ]
            self.stdout.write(self.style.SUCCESS('Sample categories created.'))
        else:
            self.stdout.write('Categories already exist.')
        # Create sample menu items for each category if missing
        for cat in categories:
            if not MenuItem.objects.filter(category=cat).exists():
                MenuItem.objects.create(category=cat, name=f'{cat.name} Sample 1', description=f'Sample {cat.name} item', price=2500, is_available=True)
                MenuItem.objects.create(category=cat, name=f'{cat.name} Sample 2', description=f'Second {cat.name} item', price=3500, is_available=True)
                self.stdout.write(self.style.SUCCESS(f'Sample menu items created for {cat.name}.'))
            else:
                self.stdout.write(f'Menu items already exist for {cat.name}.')
        self.stdout.write(self.style.SUCCESS('Sample data setup complete for Buca Republic.'))
