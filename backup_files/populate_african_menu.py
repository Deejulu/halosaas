"""
Script to populate the restaurant with authentic African menu items.
Run with: python manage.py shell < populate_african_menu.py
Or: python manage.py runscript populate_african_menu (if django-extensions installed)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from restaurants.models import Restaurant, Category, MenuItem

def populate_african_menu():
    # Get the first restaurant
    restaurant = Restaurant.objects.first()
    if not restaurant:
        print('No restaurant found!')
        return
    
    print(f'Updating menu for: {restaurant.name}')
    
    # Delete existing categories and menu items
    Category.objects.filter(restaurant=restaurant).delete()
    print('Cleared existing menu items and categories')
    
    # Create African food categories and items
    african_menu = {
        'Starters & Appetizers': {
            'description': 'Begin your journey with authentic African appetizers',
            'order': 1,
            'items': [
                {'name': 'Suya Skewers', 'description': 'Spicy grilled beef skewers seasoned with ground peanuts and traditional suya spice. A Nigerian street food favorite.', 'price': 12.99, 'prep_time': 15},
                {'name': 'Akara (Bean Cakes)', 'description': 'Crispy deep-fried black-eyed pea fritters seasoned with onions and peppers. Served with spicy pepper sauce.', 'price': 8.99, 'prep_time': 12},
                {'name': 'Samosas (Sambusa)', 'description': 'Crispy pastry triangles filled with spiced minced beef, onions and herbs. East African style.', 'price': 9.99, 'prep_time': 10},
                {'name': 'Kelewele', 'description': 'Spicy fried plantain cubes seasoned with ginger, cayenne pepper, and African spices. A Ghanaian delicacy.', 'price': 7.99, 'prep_time': 10},
                {'name': 'Puff Puff', 'description': 'Sweet Nigerian doughnuts dusted with powdered sugar. Light, fluffy, and addictive.', 'price': 6.99, 'prep_time': 15},
                {'name': 'Chin Chin', 'description': 'Crunchy fried dough snacks with a hint of nutmeg. Perfect for sharing.', 'price': 5.99, 'prep_time': 8},
            ]
        },
        'Soups & Stews': {
            'description': 'Rich, flavorful traditional African soups and stews',
            'order': 2,
            'items': [
                {'name': 'Egusi Soup', 'description': 'Rich melon seed soup with spinach, assorted meats, stockfish, and palm oil. Served with your choice of swallow.', 'price': 18.99, 'prep_time': 25},
                {'name': 'Ogbono Soup', 'description': 'Draw soup made with wild mango seeds, assorted meats, and vegetables. Thick and nutritious.', 'price': 17.99, 'prep_time': 25},
                {'name': 'Pepper Soup (Goat)', 'description': 'Spicy aromatic broth with tender goat meat, utazi leaves, and traditional pepper soup spices.', 'price': 16.99, 'prep_time': 30},
                {'name': 'Groundnut Soup', 'description': 'Creamy peanut-based soup with chicken, tomatoes, and African spices. West African comfort food.', 'price': 15.99, 'prep_time': 25},
                {'name': 'Efo Riro', 'description': 'Nigerian spinach stew with assorted meats, locust beans, and red palm oil. Rich in flavor and nutrients.', 'price': 16.99, 'prep_time': 20},
                {'name': 'Banga Soup', 'description': 'Palm fruit soup with catfish, beef, and aromatic banga spices. A Niger Delta specialty.', 'price': 19.99, 'prep_time': 30},
            ]
        },
        'Main Courses': {
            'description': 'Hearty traditional African main dishes',
            'order': 3,
            'items': [
                {'name': 'Jollof Rice (Nigerian)', 'description': 'Iconic West African one-pot rice cooked in rich tomato sauce with onions, peppers, and aromatic spices. Served with fried plantain and coleslaw.', 'price': 16.99, 'prep_time': 35},
                {'name': 'Jollof Rice (Ghanaian)', 'description': 'Smoky Ghanaian-style jollof rice with a distinct charred flavor. Served with shito and grilled chicken.', 'price': 17.99, 'prep_time': 35},
                {'name': 'Fried Rice & Chicken', 'description': 'Nigerian party-style fried rice with mixed vegetables, liver, and a quarter grilled chicken.', 'price': 18.99, 'prep_time': 30},
                {'name': 'Ofada Rice & Ayamase', 'description': 'Local brown rice served with spicy green pepper sauce (designer stew) and assorted meats.', 'price': 19.99, 'prep_time': 30},
                {'name': 'Waakye', 'description': 'Ghanaian rice and beans cooked with millet leaves. Served with shito, spaghetti, gari, and protein of choice.', 'price': 15.99, 'prep_time': 25},
                {'name': 'Thieboudienne', 'description': 'Senegalese national dish - rice cooked in tomato sauce with fish and vegetables. The original jollof!', 'price': 21.99, 'prep_time': 40},
                {'name': 'Injera Platter', 'description': 'Ethiopian sourdough flatbread served with doro wot (chicken stew), misir wot (lentils), and vegetable sides.', 'price': 22.99, 'prep_time': 35},
                {'name': 'Nyama Choma', 'description': 'Kenyan-style grilled meat (beef or goat) marinated in African spices. Served with ugali and kachumbari.', 'price': 24.99, 'prep_time': 40},
            ]
        },
        'Swallow & Accompaniments': {
            'description': 'Traditional African swallows to pair with soups',
            'order': 4,
            'items': [
                {'name': 'Pounded Yam', 'description': 'Smooth, stretchy pounded yam - the king of Nigerian swallows. Perfect with any soup.', 'price': 6.99, 'prep_time': 10},
                {'name': 'Eba (Garri)', 'description': 'Cassava flour swallow with a slightly sour taste. A popular everyday choice.', 'price': 4.99, 'prep_time': 5},
                {'name': 'Amala', 'description': 'Dark yam flour swallow with earthy flavor. Best paired with ewedu or gbegiri soup.', 'price': 5.99, 'prep_time': 8},
                {'name': 'Fufu', 'description': 'Soft cassava and plantain swallow. Smooth texture that melts in your mouth.', 'price': 5.99, 'prep_time': 10},
                {'name': 'Semovita', 'description': 'Light wheat-based swallow. Mild flavor that complements any soup.', 'price': 4.99, 'prep_time': 5},
                {'name': 'Tuwo Shinkafa', 'description': 'Northern Nigerian rice swallow. Soft and fluffy, pairs well with miyan kuka.', 'price': 5.99, 'prep_time': 10},
            ]
        },
        'Grilled & BBQ': {
            'description': 'Flame-grilled African barbecue specialties',
            'order': 5,
            'items': [
                {'name': 'Whole Grilled Tilapia', 'description': 'Whole tilapia fish grilled with onions, peppers, and African spices. Served with fried plantain.', 'price': 22.99, 'prep_time': 35},
                {'name': 'Grilled Croaker Fish', 'description': 'Fresh croaker fish seasoned and grilled to perfection. Served with pepper sauce.', 'price': 24.99, 'prep_time': 30},
                {'name': 'Asun (Spicy Goat)', 'description': 'Smoked and grilled goat meat tossed in spicy pepper sauce with onions. Absolutely irresistible.', 'price': 19.99, 'prep_time': 30},
                {'name': 'Grilled Chicken Full', 'description': 'Whole chicken marinated in African spices and grilled. Served with jollof rice or fries.', 'price': 25.99, 'prep_time': 40},
                {'name': 'Nkwobi', 'description': 'Spicy cow foot delicacy cooked in palm oil and utazi. A true Nigerian bar classic.', 'price': 21.99, 'prep_time': 35},
                {'name': 'Isi Ewu', 'description': 'Spiced goat head delicacy. Tender meat in a rich palm oil and pepper sauce.', 'price': 26.99, 'prep_time': 45},
            ]
        },
        'Vegetarian & Vegan': {
            'description': 'Plant-based African dishes full of flavor',
            'order': 6,
            'items': [
                {'name': 'Vegetable Jollof Rice', 'description': 'Classic jollof rice loaded with mixed vegetables. Vegan and delicious.', 'price': 13.99, 'prep_time': 30},
                {'name': 'Moin Moin (Beans Pudding)', 'description': 'Steamed bean pudding with peppers and onions. High protein vegetarian option.', 'price': 8.99, 'prep_time': 25},
                {'name': 'Vegetable Egusi', 'description': 'Melon seed soup prepared with mushrooms and extra vegetables. No meat, all flavor.', 'price': 14.99, 'prep_time': 25},
                {'name': 'Plantain Porridge', 'description': 'Ripe plantain cooked in palm oil with vegetables and spices. Comforting and filling.', 'price': 11.99, 'prep_time': 20},
                {'name': 'Beans & Plantain', 'description': 'Honey beans (ewa) stewed in palm oil, served with fried ripe plantain.', 'price': 12.99, 'prep_time': 25},
                {'name': 'Yam Porridge (Asaro)', 'description': 'Yam cooked in peppered palm oil sauce with onions and locust beans.', 'price': 12.99, 'prep_time': 25},
            ]
        },
        'Drinks & Beverages': {
            'description': 'Refreshing African drinks and beverages',
            'order': 7,
            'items': [
                {'name': 'Zobo (Hibiscus Drink)', 'description': 'Refreshing hibiscus flower drink with ginger, pineapple, and African spices. Served chilled.', 'price': 4.99, 'prep_time': 5},
                {'name': 'Chapman', 'description': 'Nigerian cocktail with Fanta, Sprite, grenadine, Angostura bitters, and cucumber slices.', 'price': 6.99, 'prep_time': 5},
                {'name': 'Palm Wine', 'description': 'Traditional fermented palm sap. Sweet, milky, and mildly alcoholic.', 'price': 8.99, 'prep_time': 2},
                {'name': 'Kunu (Millet Drink)', 'description': 'Creamy Northern Nigerian millet drink with ginger and cloves. Naturally sweet.', 'price': 4.99, 'prep_time': 5},
                {'name': 'Ginger Beer', 'description': 'Spicy homemade ginger beer. Strong, refreshing, and non-alcoholic.', 'price': 4.99, 'prep_time': 3},
                {'name': 'Tamarind Juice', 'description': 'Sweet and tangy tamarind drink. A popular choice across Africa.', 'price': 4.99, 'prep_time': 3},
                {'name': 'Fresh Coconut Water', 'description': 'Straight from the coconut. Pure, hydrating, and naturally sweet.', 'price': 5.99, 'prep_time': 2},
            ]
        },
        'Desserts & Sweets': {
            'description': 'Sweet endings with African flair',
            'order': 8,
            'items': [
                {'name': 'Coconut Candy', 'description': 'Chewy coconut treats caramelized with sugar. A nostalgic African sweet.', 'price': 4.99, 'prep_time': 5},
                {'name': 'Bofrot (Ghanaian Doughnuts)', 'description': 'Soft, sweet doughnuts with nutmeg flavor. Larger and fluffier than puff puff.', 'price': 6.99, 'prep_time': 15},
                {'name': 'Mandazi', 'description': 'East African fried bread triangles. Slightly sweet, perfect with tea or coffee.', 'price': 5.99, 'prep_time': 12},
                {'name': 'Malva Pudding', 'description': 'South African spongy dessert with apricot jam, served warm with custard.', 'price': 8.99, 'prep_time': 15},
                {'name': 'Banana Fritters', 'description': 'Ripe bananas coated in sweet batter and fried golden. Served with honey.', 'price': 6.99, 'prep_time': 10},
                {'name': 'Groundnut Brittle', 'description': 'Crunchy peanut candy with caramelized sugar. Traditional Nigerian sweet.', 'price': 4.99, 'prep_time': 5},
            ]
        },
    }
    
    # Create categories and items
    for cat_name, cat_data in african_menu.items():
        category = Category.objects.create(
            restaurant=restaurant,
            name=cat_name,
            description=cat_data['description'],
            order=cat_data['order']
        )
        print(f'Created category: {cat_name}')
        
        for item in cat_data['items']:
            MenuItem.objects.create(
                category=category,
                name=item['name'],
                description=item['description'],
                price=item['price'],
                preparation_time=item['prep_time'],
                is_available=True
            )
        print(f'  Added {len(cat_data["items"])} items')
    
    total_items = MenuItem.objects.filter(category__restaurant=restaurant).count()
    total_cats = Category.objects.filter(restaurant=restaurant).count()
    print(f'\nDone! Created {total_cats} categories with {total_items} menu items.')

if __name__ == '__main__':
    populate_african_menu()
