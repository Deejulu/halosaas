class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None
        cart = self.session.get('cart')

        # New format: cart is a dict mapping restaurant_id -> { item_id: item_data }
        # Old format (single dict of item_id -> item_data) will be migrated.
        if not cart:
            cart = self.session['cart'] = {}
        else:
            # Detect old flat format where keys are item ids and each value has a 'restaurant_id' key.
            # New format uses restaurant_id -> { item_id: item_data }, so the top-level values will be
            # sub-dicts (mapping item_id -> item_data) which do NOT themselves contain 'restaurant_id'.
            try:
                has_flat_items = any(
                    isinstance(v, dict) and 'restaurant_id' in v
                    for v in cart.values()
                )
            except Exception:
                has_flat_items = False

            if has_flat_items:
                migrated = {}
                for item_id, item_data in list(cart.items()):
                    # item_data expected to be a dict with a 'restaurant_id' key in the old format
                    rid = item_data.get('restaurant_id')
                    if not rid:
                        continue
                    rid = str(rid)
                    migrated.setdefault(rid, {})[str(item_id)] = item_data
                cart = self.session['cart'] = migrated

        self.cart = cart

    def _active_restaurant_id(self):
        # Current active restaurant in session, or infer when only one exists
        rid = self.session.get('current_cart_restaurant')
        if rid:
            return str(rid)
        if self.cart:
            keys = list(self.cart.keys())
            if len(keys) == 1:
                return keys[0]
        return None

    def add(self, menu_item, quantity=1, special_requests=""):
        menu_item_id = str(menu_item.id)
        restaurant_id = str(menu_item.category.restaurant.id)

        # Ensure there's a subcart for that restaurant
        if restaurant_id not in self.cart:
            self.cart[restaurant_id] = {}

        subcart = self.cart[restaurant_id]

        if menu_item_id not in subcart:
            subcart[menu_item_id] = {
                'quantity': 0,
                'price': str(menu_item.price),
                'name': menu_item.name,
                'special_requests': special_requests,
                'restaurant_id': restaurant_id,
                'restaurant_name': menu_item.category.restaurant.name
            }

        subcart[menu_item_id]['quantity'] += quantity

        # Set this restaurant as the active cart
        self.session['current_cart_restaurant'] = restaurant_id

        self.save()
        self._sync_to_database(menu_item.category.restaurant)

    def remove(self, menu_item):
        menu_item_id = str(menu_item.id)
        restaurant_id = str(menu_item.category.restaurant.id)
        subcart = self.cart.get(restaurant_id, {})
        if menu_item_id in subcart:
            del subcart[menu_item_id]
            # If subcart empty, remove restaurant key
            if not subcart:
                self.cart.pop(restaurant_id, None)
                # clear active if it was this restaurant
                if self.session.get('current_cart_restaurant') == restaurant_id:
                    self.session.pop('current_cart_restaurant', None)
            self.save()
            self._sync_to_database(menu_item.category.restaurant)

    def update(self, menu_item, quantity, special_requests=""):
        menu_item_id = str(menu_item.id)
        restaurant_id = str(menu_item.category.restaurant.id)
        subcart = self.cart.get(restaurant_id, {})
        if menu_item_id in subcart:
            subcart[menu_item_id]['quantity'] = quantity
            subcart[menu_item_id]['special_requests'] = special_requests
            if quantity <= 0:
                self.remove(menu_item)
            else:
                self.save()
                self._sync_to_database(menu_item.category.restaurant)

    def clear(self, all_restaurants=False):
        # Clear database cart for active restaurant or all
        if all_restaurants:
            # clear all saved carts for user
            if self.user and self.user.is_authenticated:
                from orders.models import SavedCart
                SavedCart.objects.filter(customer=self.user).delete()
            self.session['cart'] = {}
            self.session.pop('current_cart_restaurant', None)
            self.cart = {}
        else:
            rid = self._active_restaurant_id()
            if rid:
                # Clear DB saved cart for this restaurant
                if self.user and self.user.is_authenticated:
                    from orders.models import SavedCart
                    SavedCart.objects.filter(customer=self.user, restaurant_id=int(rid)).delete()
                self.cart.pop(rid, None)
                if self.session.get('current_cart_restaurant') == rid:
                    self.session.pop('current_cart_restaurant', None)

        self.save()

    def save(self):
        self.session.modified = True

    def _sync_to_database(self, restaurant):
        """Sync current subcart to database for admin visibility"""
        if not self.user or not self.user.is_authenticated:
            return

        from orders.models import SavedCart, SavedCartItem
        from restaurants.models import MenuItem

        try:
            restaurant_id = str(restaurant.id)
            subcart = self.cart.get(restaurant_id, {})

            # Get or create saved cart for this user/restaurant
            saved_cart, created = SavedCart.objects.get_or_create(
                customer=self.user,
                restaurant=restaurant
            )

            # Clear existing items and re-add
            saved_cart.items.all().delete()

            # Add current cart items
            for item_id, item_data in subcart.items():
                try:
                    menu_item = MenuItem.objects.get(id=int(item_id))
                    SavedCartItem.objects.create(
                        cart=saved_cart,
                        menu_item=menu_item,
                        quantity=item_data['quantity'],
                        special_requests=item_data.get('special_requests', '')
                    )
                except MenuItem.DoesNotExist:
                    pass

            # Delete saved cart if empty
            if saved_cart.items.count() == 0:
                saved_cart.delete()

        except Exception as e:
            print(f"Cart sync error: {e}")

    def _clear_database_cart(self):
        """Clear the database cart for active restaurant"""
        if not self.user or not self.user.is_authenticated:
            return

        from orders.models import SavedCart

        try:
            restaurant_id = self._active_restaurant_id()
            if restaurant_id:
                SavedCart.objects.filter(
                    customer=self.user,
                    restaurant_id=int(restaurant_id)
                ).delete()
        except Exception as e:
            print(f"Cart clear error: {e}")

    def get_total_price(self):
        rid = self._active_restaurant_id()
        if not rid:
            return 0
        subcart = self.cart.get(rid, {})
        return sum(float(item['price']) * item['quantity'] for item in subcart.values())

    def get_total_items(self):
        rid = self._active_restaurant_id()
        if not rid:
            return 0
        subcart = self.cart.get(rid, {})
        return sum(item['quantity'] for item in subcart.values())

    def get_restaurant_id(self):
        return self._active_restaurant_id()

    def __iter__(self):
        rid = self._active_restaurant_id()
        if not rid:
            return
        subcart = self.cart.get(rid, {})
        for item_id, item_data in subcart.items():
            yield {
                'menu_item_id': item_id,
                'quantity': item_data['quantity'],
                'price': float(item_data['price']),
                'total_price': float(item_data['price']) * item_data['quantity'],
                'name': item_data['name'],
                'special_requests': item_data['special_requests'],
                'restaurant_name': item_data['restaurant_name']
            }

    def __len__(self):
        return self.get_total_items()