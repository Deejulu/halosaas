"""
Context processors to make notification data available globally in templates
"""
from django.utils import timezone


def user_notifications(request):
    """
    Provide notification counts for all user roles.
    
    For Admins:
    - admin_total_pending_orders: All pending orders across platform
    - admin_total_active_carts: All active carts across platform
    - admin_today_orders: All orders placed today
    - admin_new_restaurants: Restaurants added this week
    - admin_total_notifications: Total notification count
    
    For Restaurant Owners:
    - owner_pending_orders: Pending orders for their restaurants
    - owner_active_carts: Active carts for their restaurants
    - owner_today_orders: Today's orders for their restaurants
    - owner_total_notifications: Total notification count
    
    For Customers:
    - customer_active_orders: Orders that are pending/preparing/ready
    - customer_cart_items: Items in current cart
    - customer_total_notifications: Total notification count
    """
    context = {
        # Admin notifications
        'admin_total_pending_orders': 0,
        'admin_total_active_carts': 0,
        'admin_today_orders': 0,
        'admin_new_restaurants': 0,
        'admin_total_notifications': 0,
        # Restaurant owner notifications
        'owner_pending_orders': 0,
        'owner_active_carts': 0,
        'owner_total_notifications': 0,
        'owner_today_orders': 0,
        # Customer notifications
        'customer_active_orders': 0,
        'customer_cart_items': 0,
        'customer_total_notifications': 0,
    }
    
    if not request.user.is_authenticated:
        return context
    
    try:
        from restaurants.models import Restaurant
        from orders.models import Order, SavedCart
        from datetime import timedelta
        
        user = request.user
        
        # ========== ADMIN NOTIFICATIONS ==========
        if user.role == 'admin':
            # All pending orders across platform
            admin_pending = Order.objects.filter(status='pending').count()
            
            # All active carts
            admin_carts = SavedCart.objects.count()
            
            # Today's orders
            admin_today = Order.objects.filter(
                created_at__date=timezone.now().date()
            ).count()
            
            # New restaurants this week
            week_ago = timezone.now() - timedelta(days=7)
            new_restaurants = Restaurant.objects.filter(
                created_at__gte=week_ago
            ).count()
            
            context.update({
                'admin_total_pending_orders': admin_pending,
                'admin_total_active_carts': admin_carts,
                'admin_today_orders': admin_today,
                'admin_new_restaurants': new_restaurants,
                'admin_total_notifications': admin_pending + admin_carts,
            })
        
        # ========== RESTAURANT OWNER NOTIFICATIONS ==========
        elif user.role == 'restaurant_owner':
            restaurants = Restaurant.objects.filter(owner=user)
            
            if restaurants.exists():
                pending_orders = Order.objects.filter(
                    restaurant__in=restaurants,
                    status='pending'
                ).count()
                
                active_carts = SavedCart.objects.filter(
                    restaurant__in=restaurants
                ).count()
                
                today_orders = Order.objects.filter(
                    restaurant__in=restaurants,
                    created_at__date=timezone.now().date()
                ).count()
                
                context.update({
                    'owner_pending_orders': pending_orders,
                    'owner_active_carts': active_carts,
                    'owner_total_notifications': pending_orders + active_carts,
                    'owner_today_orders': today_orders,
                })
        
        # ========== CUSTOMER NOTIFICATIONS ==========
        elif user.role == 'customer':
            # Active orders (not delivered or cancelled) across all restaurants
            active_orders = Order.objects.filter(
                customer=user,
                status__in=['pending', 'confirmed', 'preparing', 'ready']
            ).count()

            # Cart items from session (support new per-restaurant cart format)
            cart_items = 0
            active_cart_restaurant = None
            cart = request.session.get('cart', {}) or {}
            # New format: { restaurant_id: { item_id: data } }
            current_rid = request.session.get('current_cart_restaurant')
            if current_rid and str(current_rid) in cart:
                sub = cart.get(str(current_rid), {})
                cart_items = sum(item.get('quantity', 0) for item in sub.values())
                active_cart_restaurant = None
                # try to get restaurant name from one of the items
                if sub:
                    first = next(iter(sub.values()))
                    active_cart_restaurant = first.get('restaurant_name')
            else:
                # fallback: sum across all subcarts
                total = 0
                for sub in cart.values():
                    if isinstance(sub, dict):
                        total += sum(item.get('quantity', 0) for item in sub.values())
                cart_items = total

            context.update({
                'customer_active_orders': active_orders,
                'customer_cart_items': cart_items,
                'customer_cart_restaurant': active_cart_restaurant,
                'customer_total_notifications': active_orders,
            })
            
    except Exception as e:
        print(f"Notification context error: {e}")
    
    return context


# Keep old function name for backwards compatibility
def owner_notifications(request):
    """Backwards compatible - calls user_notifications"""
    return user_notifications(request)
