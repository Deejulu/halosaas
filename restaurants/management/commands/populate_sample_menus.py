from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, MenuItem, Category

SAMPLE_MENUS = {
    'Naija Grill House': [
        {
            'category': 'Starters',
            'description': 'Small bites to get you started',
            'items': [
                {'name': 'Lagos Suya Skewers', 'description': 'Beef and chicken suya, thinly sliced and spicy.', 'price': 1200, 'prep_time': 8},
                {'name': 'Suya Onion Salad', 'description': 'Fresh sliced onion with yaji and cucumber.', 'price': 400, 'prep_time': 2},
                {'name': 'Spiced Plantain Bites', 'description': 'Fried plantain with pepper dip.', 'price': 600, 'prep_time': 6},
            ]
        },
        {
            'category': 'Mains',
            'description': 'Grilled and charcoal specialties',
            'items': [
                {'name': 'Grilled Catfish', 'description': 'Whole catfish with house spice rub and pepper sauce.', 'price': 5000, 'prep_time': 25},
                {'name': 'Jollof Fiesta Platter', 'description': 'Smoky jollof rice, grilled turkey, fried plantain.', 'price': 3500, 'prep_time': 20},
            ]
        },
        {
            'category': 'Sides',
            'description': 'Perfect complements',
            'items': [
                {'name': 'Fried Plantain', 'description': 'Sweet and crispy dodo.', 'price': 700, 'prep_time': 6},
                {'name': 'Pepper Sauce', 'description': 'Signature spicy pepper sauce.', 'price': 200, 'prep_time': 1},
            ]
        },
        {
            'category': 'Drinks',
            'description': 'Local and chilled',
            'items': [
                {'name': 'Palmwine (Small)', 'description': 'Freshly tapped palmwine.', 'price': 800, 'prep_time': 0},
                {'name': 'Chapman', 'description': 'Classic Nigerian soft cocktail.', 'price': 900, 'prep_time': 3},
            ]
        }
    ],
    'Bukka Republic': [
        {
            'category': 'Soups & Stews',
            'description': 'Traditional Yoruba soups and stews',
            'items': [
                {'name': 'Efo Riro Supreme', 'description': 'Spinach stew with assorted meats and fish.', 'price': 3500, 'prep_time': 18},
                {'name': 'Gbegiri & Amala', 'description': 'Rich bean soup served with amala.', 'price': 3200, 'prep_time': 20},
            ]
        },
        {
            'category': 'Combos',
            'description': 'Hearty combinations',
            'items': [
                {'name': 'Amala Gbegiri Combo', 'description': 'Amala, gbegiri, ewedu with assorted meat.', 'price': 3800, 'prep_time': 20},
            ]
        },
        {
            'category': 'Drinks',
            'description': 'House beverages',
            'items': [
                {'name': 'Zobo (Hibiscus)', 'description': 'Refreshing zobo with ginger.', 'price': 700, 'prep_time': 2},
            ]
        }
    ],
    'Jollof City': [
        {
            'category': 'Jollof Specials',
            'description': 'Different proteins with our coal-city jollof',
            'items': [
                {'name': 'Smoky Jollof Rice (Chicken)', 'description': 'Smoky jollof with charred chicken.', 'price': 3400, 'prep_time': 18},
                {'name': 'Smoky Jollof Rice (Beef)', 'description': 'Smoky jollof with braised beef.', 'price': 3600, 'prep_time': 20},
            ]
        },
        {
            'category': 'Sides',
            'description': 'Classic sides',
            'items': [
                {'name': 'Moi Moi Deluxe', 'description': 'Steamed bean pudding with fillings.', 'price': 1800, 'prep_time': 30},
                {'name': 'Fried Croaker', 'description': 'Crispy croaker with pepper dip.', 'price': 4200, 'prep_time': 22},
            ]
        },
        {
            'category': 'Drinks',
            'description': 'Local cocktails',
            'items': [
                {'name': 'Chapman', 'description': 'Bittersweet cocktail with garnish.', 'price': 1500, 'prep_time': 3},
            ]
        }
    ],
    'Palmwine Place': [
        {
            'category': 'Main Plates',
            'description': 'Igbo favorites and palmwine pairings',
            'items': [
                {'name': 'Isi Ewu', 'description': 'Spicy goat head served with utazi.', 'price': 5000, 'prep_time': 35},
                {'name': 'Nkwobi', 'description': 'Seasoned cow foot in palm oil.', 'price': 4200, 'prep_time': 30},
            ]
        },
        {
            'category': 'Drinks',
            'description': 'Fresh palmwine and accompaniments',
            'items': [
                {'name': 'Palmwine Jug (Medium)', 'description': 'Shared palmwine jug.', 'price': 2000, 'prep_time': 0},
            ]
        }
    ],
    'Pepper Soup Spot': [
        {
            'category': 'Soups',
            'description': 'Hot, restorative soups from the Delta',
            'items': [
                {'name': 'Catfish Pepper Soup', 'description': 'Spicy catfish soup with scent leaves.', 'price': 3700, 'prep_time': 15},
                {'name': 'Chicken Pepper Soup', 'description': 'Aromatic chicken broth with herbs.', 'price': 3400, 'prep_time': 14},
            ]
        },
        {
            'category': 'Comfort',
            'description': 'Hearty plates to warm you',
            'items': [
                {'name': 'Yam Porridge', 'description': 'Yam cooked in palm oil with fish.', 'price': 2800, 'prep_time': 25},
            ]
        }
    ],
    'Chop Life Lounge': [
        {
            'category': 'Grill & Share',
            'description': 'Party style plates and sharables',
            'items': [
                {'name': 'Asun Deluxe', 'description': 'Smoky peppered goat, onions, peppers.', 'price': 4800, 'prep_time': 18},
                {'name': 'Grilled Prawns', 'description': 'Charcoal grilled prawns with lemon butter.', 'price': 6000, 'prep_time': 20},
            ]
        },
        {
            'category': 'Drinks',
            'description': 'Trendy bar beverages',
            'items': [
                {'name': 'Tigernut Punch', 'description': 'Creamy tigernut and coconut punch.', 'price': 1200, 'prep_time': 5},
            ]
        }
    ],
    'Ofada Kitchen': [
        {
            'category': 'Ofada Specials',
            'description': 'Local rice dishes and rich stews',
            'items': [
                {'name': 'Ofada Rice & Designer Stew', 'description': 'Local rice served with ayamase and assorted meat.', 'price': 4000, 'prep_time': 25},
                {'name': 'Stewed Snails', 'description': 'Snails in rich pepper-tomato stew.', 'price': 5000, 'prep_time': 30},
            ]
        },
        {
            'category': 'Sides & Drinks',
            'description': 'Traditional sides and drinks',
            'items': [
                {'name': 'Fried Dodo', 'description': 'Sweet fried plantain.', 'price': 1500, 'prep_time': 6},
                {'name': 'Kunu', 'description': 'Chilled millet drink.', 'price': 800, 'prep_time': 2},
            ]
        }
    ],
}

class Command(BaseCommand):
    help = 'Populate beautiful sample menu items for each restaurant.'

    def handle(self, *args, **options):
        # Optional style updates per restaurant for visual testing
        STYLE_UPDATES = {
            'Naija Grill House': {'primary_color': '#e25822', 'secondary_color': '#f7b731', 'menu_layout': 'grid'},
            'Bukka Republic': {'primary_color': '#2e8b57', 'secondary_color': '#daa520', 'menu_layout': 'list'},
            'Jollof City': {'primary_color': '#dc143c', 'secondary_color': '#ffd700', 'menu_layout': 'compact'},
            'Palmwine Place': {'primary_color': '#8b4513', 'secondary_color': '#deb887', 'menu_layout': 'masonry'},
            'Pepper Soup Spot': {'primary_color': '#ff4500', 'secondary_color': '#32cd32', 'menu_layout': 'large'},
            'Chop Life Lounge': {'primary_color': '#4b0082', 'secondary_color': '#9370db', 'menu_layout': 'grid'},
            'Ofada Kitchen': {'primary_color': '#228b22', 'secondary_color': '#f4a460', 'menu_layout': 'list'},
        }

        for restaurant in Restaurant.objects.all():
            menu_def = SAMPLE_MENUS.get(restaurant.name)
            # Apply visual style overrides if present
            style = STYLE_UPDATES.get(restaurant.name)
            if style:
                for k, v in style.items():
                    setattr(restaurant, k, v)
                restaurant.save()

            if not menu_def:
                # skip if no structured menu defined
                self.stdout.write(self.style.WARNING(f"No structured menu for {restaurant.name}, skipping."))
                continue

            total_items = 0
            for cat_def in menu_def:
                cat_name = cat_def.get('category', 'Main Dishes')
                cat_desc = cat_def.get('description', '')
                category, _ = Category.objects.get_or_create(
                    restaurant=restaurant,
                    name=cat_name,
                    defaults={'description': cat_desc}
                )
                for item in cat_def.get('items', []):
                    MenuItem.objects.get_or_create(
                        category=category,
                        name=item['name'],
                        defaults={
                            'description': item.get('description', ''),
                            'price': item.get('price', 0),
                            'is_available': True,
                            'preparation_time': item.get('prep_time', 10),
                        }
                    )
                    total_items += 1

            self.stdout.write(self.style.SUCCESS(f"✅ {total_items} items added for {restaurant.name}"))
        self.stdout.write(self.style.SUCCESS("All sample menus created!"))
