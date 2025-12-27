from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from restaurants.models import Restaurant, Category, MenuItem
from orders.models import Order, SavedCart
from accounts.models import CustomUser
from payments.models import Payment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta
import csv
import json

# Home page view
def home(request):
    """Home page with featured restaurants"""
    featured_restaurants = Restaurant.objects.filter(is_active=True)[:6]
    # Sample items for the hero mockup (fallback to currently available menu items)
    sample_items = MenuItem.objects.filter(is_available=True).select_related('category', 'category__restaurant')[:4]
    sample_total = sum(float(i.price) for i in sample_items) if sample_items else 0

    # Top sellers: aggregate OrderItem quantities
    try:
        from orders.models import OrderItem
        top_seller_ids = (
            OrderItem.objects.values('menu_item')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')
            .values_list('menu_item', flat=True)[:4]
        )
        top_sellers = list(MenuItem.objects.filter(id__in=list(top_seller_ids)).select_related('category')[:4])
    except Exception:
        top_sellers = list(MenuItem.objects.filter(is_available=True).select_related('category')[:4])

    # Today's specials: recently created items (last 14 days)
    two_weeks_ago = timezone.now() - timedelta(days=14)
    todays_specials = list(MenuItem.objects.filter(is_available=True, created_at__gte=two_weeks_ago).select_related('category')[:4])

    # Combo deals / customer picks: fallback to latest available items
    customer_picks = list(MenuItem.objects.filter(is_available=True).select_related('category').order_by('-created_at')[:4])

    context = {
        'featured_restaurants': featured_restaurants,
        'sample_items': sample_items,
        'sample_total': sample_total,
        'top_sellers': top_sellers,
        'todays_specials': todays_specials,
        'customer_picks': customer_picks,
    }
    return render(request, 'core/home.html', context)

def browse_restaurants(request):
    """Browse all active restaurants with search and filters"""
    restaurants = Restaurant.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        restaurants = restaurants.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).distinct()
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        restaurants = restaurants.filter(category__name__iexact=category_filter)
    
    # Get unique categories for filter dropdown
    categories = Category.objects.filter(restaurant__is_active=True).values_list('name', flat=True).distinct()
    
    context = {
        'restaurants': restaurants,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'total_restaurants': restaurants.count(),
    }
    return render(request, 'core/browse_restaurants.html', context)

@login_required
def dashboard(request):
    """Redirect users to their appropriate dashboard"""
    user = request.user
    print(f"🎯 DASHBOARD ROUTING: {user.username} → {user.role}")
    
    # Clear welcome overlay session flag if requested
    if user.role == 'customer':
        if request.method == 'GET' and request.GET.get('clear_welcome') == '1':
            if 'show_welcome_overlay' in request.session:
                del request.session['show_welcome_overlay']
        elif request.method == 'POST' and request.GET.get('clear_welcome') == '0':
            if 'show_welcome_overlay' in request.session:
                del request.session['show_welcome_overlay']
            return JsonResponse({'cleared': True})
        # CUSTOMER DASHBOARD - Enhanced with more data
        
        # All orders for this customer
        all_orders = Order.objects.filter(customer=user)
        recent_orders = all_orders.order_by('-created_at')[:5]
        
        # Order statistics
        total_orders = all_orders.count()
        completed_orders = all_orders.filter(status__in=['confirmed', 'completed']).count()
        pending_orders = all_orders.filter(status__in=['pending', 'awaiting_confirmation', 'confirmed', 'preparing', 'ready']).count()
        cancelled_orders = all_orders.filter(status='cancelled').count()
        
        # Calculate total spent (confirmed and completed)
        total_spent = all_orders.filter(status__in=['confirmed', 'completed']).aggregate(Sum('total_price'))['total_price__sum'] or 0

        # This month's spending (confirmed and completed)
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_spent = all_orders.filter(
            status__in=['confirmed', 'completed'],
            created_at__gte=first_day_of_month
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Favorite restaurants (most ordered from)
        favorite_restaurants = all_orders.values(
            'restaurant__id', 'restaurant__name', 'restaurant__slug', 'restaurant__logo'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_price')
        ).order_by('-order_count')[:3]
        
        # Payment method breakdown
        payment_methods = all_orders.values('payment_method').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent activity (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        recent_activity_count = all_orders.filter(created_at__gte=last_week).count()
        
        # Featured restaurants
        featured_restaurants = Restaurant.objects.filter(is_active=True)[:6]
        
        # Reviews given by customer
        from orders.models import Review
        reviews_given = Review.objects.filter(order__customer=user).count() if hasattr(Review, 'objects') else 0
        
        # Active orders (not completed or cancelled)
        active_orders = all_orders.filter(
            status__in=['pending', 'awaiting_confirmation', 'confirmed', 'preparing', 'ready']
        ).order_by('-created_at')[:3]
        
        context = {
            'user': user,
            'recent_orders': recent_orders,
            'active_orders': active_orders,
            'featured_restaurants': featured_restaurants,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'cancelled_orders': cancelled_orders,
            'total_spent': total_spent,
            'monthly_spent': monthly_spent,
            'favorite_restaurants': favorite_restaurants,
            'payment_methods': payment_methods,
            'recent_activity_count': recent_activity_count,
            'reviews_given': reviews_given,
        }
        return render(request, 'core/customer_dashboard.html', context)
    
    elif user.role == 'restaurant_owner':
        # REDIRECT to existing restaurant dashboard
        return redirect('restaurant_dashboard')
    
    elif user.role == 'admin' or user.is_superuser or user.is_staff:
        # ADMIN DASHBOARD - COMPLETE DATA
        # Allow Django superusers/staff to access the admin dashboard even if
        # their `role` field hasn't been set to 'admin'. This ensures created
        # superusers (is_superuser=True) are routed here.
        # Platform-wide analytics
        total_restaurants = Restaurant.objects.count()
        total_users = CustomUser.objects.count()
        total_orders = Order.objects.count()
        
        # User counts by role - Use ONLY the role field (no duplicates)
        user_counts = {
            'admin': CustomUser.objects.filter(role='admin').count(),
            'owner': CustomUser.objects.filter(role='restaurant_owner').count(),
            'customer': CustomUser.objects.filter(role='customer').count(),
        }
        
        # Get ALL users (not just restaurant owners)
        all_users = CustomUser.objects.select_related().order_by('-date_joined')

        # Role-specific querysets - Use ONLY role field (each user in one list only)
        admin_users = CustomUser.objects.filter(role='admin').order_by('-date_joined')
        owner_users = CustomUser.objects.filter(role='restaurant_owner').order_by('-date_joined')
        customer_users = CustomUser.objects.filter(role='customer').order_by('-date_joined')
        
        # Get restaurants with their owners
        restaurants_with_owners = Restaurant.objects.select_related('owner').all()
        
        # Revenue analytics
        total_revenue = Payment.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
        today_revenue = Payment.objects.filter(
            status='success',
            created_at__date=timezone.now().date()
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Additional metrics for better admin overview
        today = timezone.now().date()
        this_week_start = today - timedelta(days=today.weekday())
        this_month_start = today.replace(day=1)
        
        # Today's stats
        today_orders = Order.objects.filter(created_at__date=today).count()
        pending_orders = Order.objects.filter(status='pending').count()
        new_users_today = CustomUser.objects.filter(date_joined__date=today).count()
        new_users_week = CustomUser.objects.filter(date_joined__date__gte=this_week_start).count()
        
        # Order stats
        completed_orders = Order.objects.filter(status='completed').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        avg_order_value = Order.objects.filter(status='completed').aggregate(Avg('total_price'))['total_price__avg'] or 0
        
        # This week/month revenue
        week_revenue = Payment.objects.filter(
            status='success',
            created_at__date__gte=this_week_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        month_revenue = Payment.objects.filter(
            status='success',
            created_at__date__gte=this_month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Recent activity
        recent_orders = Order.objects.select_related('restaurant', 'customer').order_by('-created_at')[:10]
        recent_restaurants = Restaurant.objects.select_related('owner').order_by('-created_at')[:5]
        
        # Admin-only analytics
        active_restaurants = Restaurant.objects.filter(is_active=True).count()
        suspended_restaurants = Restaurant.objects.filter(is_active=False).count()
        
        # Restaurant Owner Overview Data
        # Get all restaurant owners with their restaurants, orders and carts
        owner_overview = []
        for owner in owner_users:
            owner_restaurants = Restaurant.objects.filter(owner=owner).prefetch_related('order_set')
            owner_data = {
                'owner': owner,
                'restaurants': [],
                'total_orders': 0,
                'total_revenue': 0,
                'active_carts': 0,
            }
            
            for restaurant in owner_restaurants:
                orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')
                carts = SavedCart.objects.filter(restaurant=restaurant).select_related('customer').prefetch_related('items')
                restaurant_revenue = orders.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
                
                owner_data['restaurants'].append({
                    'restaurant': restaurant,
                    'orders': orders[:5],  # Recent 5 orders
                    'orders_count': orders.count(),
                    'pending_orders': orders.filter(status='pending').count(),
                    'carts': carts,
                    'carts_count': carts.count(),
                    'revenue': restaurant_revenue,
                })
                owner_data['total_orders'] += orders.count()
                owner_data['total_revenue'] += restaurant_revenue
                owner_data['active_carts'] += carts.count()
            
            if owner_restaurants.exists():
                owner_overview.append(owner_data)
        
        # All active carts across the platform
        all_active_carts = SavedCart.objects.select_related('customer', 'restaurant').prefetch_related('items__menu_item').order_by('-updated_at')
        
        context = {
            'user': user,
            # Basic stats
            'total_restaurants': total_restaurants,
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'today_revenue': today_revenue,
            
            # Additional metrics
            'today_orders': today_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'avg_order_value': avg_order_value,
            'week_revenue': week_revenue,
            'month_revenue': month_revenue,
            
            # User management data - FIXED: ADD user_counts
            'user_counts': user_counts,
            'all_users': all_users,
            'admin_users': admin_users,
            'owner_users': owner_users,
            'customer_users': customer_users,
            'restaurants_with_owners': restaurants_with_owners,
            
            # Admin controls
            'active_restaurants': active_restaurants,
            'suspended_restaurants': suspended_restaurants,
            'recent_orders': recent_orders,
            'recent_restaurants': recent_restaurants,
            
            # Restaurant Owner Overview
            'owner_overview': owner_overview,
            'all_active_carts': all_active_carts,
        }
        return render(request, 'core/admin_dashboard.html', context)
    
    else:
        # Fallback
        context = {'user': user}
        return render(request, 'core/customer_dashboard.html', context)

@login_required
def add_restaurant(request):
    """Add new restaurant - Owner only"""
    if request.user.role != 'restaurant_owner' and request.user.role != 'admin':
        messages.error(request, "You don't have permission to add restaurants.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name')
            description = request.POST.get('description')
            address = request.POST.get('address')
            phone = request.POST.get('phone')
            email = request.POST.get('email', '')
            opening_time = request.POST.get('opening_time')
            closing_time = request.POST.get('closing_time')
            
            # About Section fields
            about_title = request.POST.get('about_title', 'Our Story')
            about_content = request.POST.get('about_content', '')
            chef_name = request.POST.get('chef_name', '')
            chef_bio = request.POST.get('chef_bio', '')
            
            # Social Media fields
            website = request.POST.get('website', '')
            facebook = request.POST.get('facebook', '')
            instagram = request.POST.get('instagram', '')
            twitter = request.POST.get('twitter', '')
            
            # Payment fields
            accepts_cash = request.POST.get('accepts_cash') == 'on'
            accepts_card = request.POST.get('accepts_card') == 'on'
            accepts_bank_transfer = request.POST.get('accepts_bank_transfer') == 'on'
            accepts_mobile_money = request.POST.get('accepts_mobile_money') == 'on'
            accepts_paystack = request.POST.get('accepts_paystack') == 'on'
            accepts_pos = request.POST.get('accepts_pos') == 'on'
            bank_name = request.POST.get('bank_name', '')
            bank_account_number = request.POST.get('bank_account_number', '')
            bank_account_name = request.POST.get('bank_account_name', '')
            mobile_money_provider = request.POST.get('mobile_money_provider', '')
            mobile_money_number = request.POST.get('mobile_money_number', '')
            
            # Create restaurant
            restaurant = Restaurant.objects.create(
                owner=request.user,
                name=name,
                description=description,
                address=address,
                phone=phone,
                email=email or request.user.email,
                opening_time=opening_time,
                closing_time=closing_time,
                about_title=about_title,
                about_content=about_content,
                chef_name=chef_name,
                chef_bio=chef_bio,
                website=website,
                facebook=facebook,
                instagram=instagram,
                twitter=twitter,
                accepts_cash=accepts_cash,
                accepts_card=accepts_card,
                accepts_bank_transfer=accepts_bank_transfer,
                accepts_mobile_money=accepts_mobile_money,
                accepts_paystack=accepts_paystack,
                accepts_pos=accepts_pos,
                bank_name=bank_name,
                bank_account_number=bank_account_number,
                bank_account_name=bank_account_name,
                mobile_money_provider=mobile_money_provider,
                mobile_money_number=mobile_money_number,
                is_active=True
            )
            
            # Handle file uploads
            if 'logo' in request.FILES:
                restaurant.logo = request.FILES['logo']
            if 'banner_image' in request.FILES:
                restaurant.banner_image = request.FILES['banner_image']
            if 'chef_image' in request.FILES:
                restaurant.chef_image = request.FILES['chef_image']
            restaurant.save()
            
            messages.success(request, f'Restaurant "{name}" created successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating restaurant: {str(e)}')
    
    return render(request, 'core/add_restaurant.html')

@login_required
def edit_restaurant(request, restaurant_id):
    """Edit restaurant details - Owner only"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check permission - owner or admin can edit
    if request.user != restaurant.owner and request.user.role != 'admin':
        messages.error(request, "You don't have permission to edit this restaurant.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Update restaurant fields
            restaurant.name = request.POST.get('name', restaurant.name)
            restaurant.description = request.POST.get('description', restaurant.description)
            restaurant.address = request.POST.get('address', restaurant.address)
            restaurant.phone = request.POST.get('phone', restaurant.phone)
            restaurant.email = request.POST.get('email', restaurant.email)
            restaurant.opening_time = request.POST.get('opening_time', restaurant.opening_time)
            restaurant.closing_time = request.POST.get('closing_time', restaurant.closing_time)
            restaurant.is_active = request.POST.get('is_active') == 'on'
            
            # About Section fields
            restaurant.about_title = request.POST.get('about_title', restaurant.about_title)
            restaurant.about_content = request.POST.get('about_content', restaurant.about_content)
            restaurant.chef_name = request.POST.get('chef_name', restaurant.chef_name)
            restaurant.chef_bio = request.POST.get('chef_bio', restaurant.chef_bio)
            
            # Social Media fields
            restaurant.website = request.POST.get('website', restaurant.website)
            restaurant.facebook = request.POST.get('facebook', restaurant.facebook)
            restaurant.instagram = request.POST.get('instagram', restaurant.instagram)
            restaurant.twitter = request.POST.get('twitter', restaurant.twitter)
            
            # Payment fields
            restaurant.accepts_cash = request.POST.get('accepts_cash') == 'on'
            restaurant.accepts_card = request.POST.get('accepts_card') == 'on'
            restaurant.accepts_bank_transfer = request.POST.get('accepts_bank_transfer') == 'on'
            restaurant.accepts_mobile_money = request.POST.get('accepts_mobile_money') == 'on'
            restaurant.accepts_paystack = request.POST.get('accepts_paystack') == 'on'
            restaurant.accepts_pos = request.POST.get('accepts_pos') == 'on'
            restaurant.bank_name = request.POST.get('bank_name', restaurant.bank_name)
            restaurant.bank_account_number = request.POST.get('bank_account_number', restaurant.bank_account_number)
            restaurant.bank_account_name = request.POST.get('bank_account_name', restaurant.bank_account_name)
            restaurant.mobile_money_provider = request.POST.get('mobile_money_provider', restaurant.mobile_money_provider)
            restaurant.mobile_money_number = request.POST.get('mobile_money_number', restaurant.mobile_money_number)
            
            # Handle file uploads
            if 'logo' in request.FILES:
                restaurant.logo = request.FILES['logo']
            if 'banner_image' in request.FILES:
                restaurant.banner_image = request.FILES['banner_image']
            if 'chef_image' in request.FILES:
                restaurant.chef_image = request.FILES['chef_image']
            
            restaurant.save()
            messages.success(request, f'Restaurant "{restaurant.name}" updated successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error updating restaurant: {str(e)}')
    
    context = {
        'restaurant': restaurant,
    }
    return render(request, 'core/edit_restaurant.html', context)

@login_required
def delete_restaurant(request, restaurant_id):
    """Delete restaurant - Owner only"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check permission
    if request.user != restaurant.owner and request.user.role != 'admin':
        messages.error(request, "You don't have permission to delete this restaurant.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        restaurant_name = restaurant.name
        restaurant.delete()
        messages.success(request, f'Restaurant "{restaurant_name}" deleted successfully!')
        return redirect('dashboard')
    
    context = {
        'restaurant': restaurant,
    }
    return render(request, 'core/delete_restaurant.html', context)

@login_required
def manage_menu(request, restaurant_id):
    """Manage restaurant menu items and categories - Owner only"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check permission
    if request.user != restaurant.owner and request.user.role != 'admin':
        messages.error(request, "You don't have permission to manage this menu.")
        return redirect('dashboard')
    
    # Get menu items and categories for this restaurant
    categories = Category.objects.filter(restaurant=restaurant)
    menu_items = MenuItem.objects.filter(category__restaurant=restaurant)
    
    # Calculate stats - FIXED: Add proper calculations
    total_items = menu_items.count()
    available_items = menu_items.filter(is_available=True).count()
    
    # Calculate revenue from completed orders
    completed_orders = Order.objects.filter(
        restaurant=restaurant, 
        status='completed'
    )
    total_revenue = sum(order.total_price for order in completed_orders)
    
    if request.method == 'POST':
        # Handle menu item creation - FIXED: Correct logic
        if 'add_menu_item' in request.POST:
            try:
                category = Category.objects.get(
                    id=request.POST.get('item_category'),
                    restaurant=restaurant
                )
                MenuItem.objects.create(
                    category=category,
                    name=request.POST.get('item_name'),
                    description=request.POST.get('item_description', ''),
                    price=request.POST.get('item_price'),
                    preparation_time=request.POST.get('preparation_time', 15),
                    is_available=True
                )
                messages.success(request, 'Menu item added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding menu item: {str(e)}')
        
        # Handle category creation
        elif 'add_category' in request.POST:
            try:
                Category.objects.create(
                    restaurant=restaurant,
                    name=request.POST.get('category_name'),
                    description=request.POST.get('category_description', '')
                )
                messages.success(request, 'Category added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding category: {str(e)}')
    
    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'categories': categories,
        'total_items': total_items,
        'available_items': available_items,
        'total_revenue': total_revenue,
    }
    return render(request, 'restaurants/manage_menu.html', context)

# ORDER MANAGEMENT VIEWS
@login_required
def order_management(request):
    """Order management page - Different data based on role"""
    user = request.user
    context = {}
    
    if user.role == 'restaurant_owner':
        # Owner sees only their restaurant orders
        orders = Order.objects.filter(restaurant__owner=user).order_by('-created_at')
        context['orders'] = orders
        context['page_title'] = 'My Restaurant Orders'
        
    elif user.role == 'admin':
        # Admin sees all orders
        orders = Order.objects.all().order_by('-created_at')
        context['orders'] = orders
        context['page_title'] = 'All Platform Orders'
        
    elif user.role == 'customer':
        # Customer sees only their orders
        orders = Order.objects.filter(customer=user).order_by('-created_at')
        context['orders'] = orders
        context['page_title'] = 'My Orders'
    
    else:
        orders = Order.objects.none()
    
    context['total_orders'] = orders.count()
    context['pending_orders'] = orders.filter(status='pending').count()
    context['completed_orders'] = orders.filter(status='completed').count()
    
    return render(request, 'core/order_management.html', context)

@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permission
    user = request.user
    if (user.role == 'customer' and order.customer != user) and \
       (user.role == 'restaurant_owner' and order.restaurant.owner != user) and \
       (user.role != 'admin'):
        messages.error(request, "You don't have permission to view this order.")
        return redirect('dashboard')
    
    context = {
        'order': order,
        'order_items': order.orderitem_set.all(),
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def update_order_status(request, order_id):
    """Update order status - Owner and Admin only"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permission - owner or admin can update status
    if request.user != order.restaurant.owner and request.user.role != 'admin':
        messages.error(request, "You don't have permission to update this order.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('order_detail', order_id=order_id)


# ============================================================================
# ANALYTICS VIEWS
# ============================================================================
@login_required
def analytics_dashboard(request):
    """Enhanced analytics dashboard with charts and time filters"""
    user = request.user
    context = {'user': user}
    
    # Time period filter
    time_period = request.GET.get('period', 'week')
    context['time_period'] = time_period
    
    # Calculate date ranges
    today = timezone.now().date()
    if time_period == 'today':
        start_date = today
        end_date = today
    elif time_period == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif time_period == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    else:  # all_time
        start_date = None
        end_date = today
    
    if user.role == 'admin':
        # ADMIN ANALYTICS - Enhanced with time filters
        from accounts.models import CustomUser
        from restaurants.models import Restaurant
        from orders.models import Order
        from payments.models import Payment
        
        # Base queries with time filter
        date_filter = Q()
        if start_date:
            date_filter = Q(created_at__date__range=[start_date, end_date])
        
        # Platform metrics with time filter
        total_restaurants = Restaurant.objects.count()
        total_users = CustomUser.objects.count()
        total_orders = Order.objects.filter(date_filter).count() if start_date else Order.objects.count()
        
        # Revenue analytics
        revenue_filter = Q(status='success')
        if start_date:
            revenue_filter &= Q(created_at__date__range=[start_date, end_date])
            
        total_revenue = Payment.objects.filter(revenue_filter).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Growth metrics
        new_users = CustomUser.objects.filter(date_joined__date__range=[start_date, end_date]).count() if start_date else 0
        new_restaurants = Restaurant.objects.filter(created_at__date__range=[start_date, end_date]).count() if start_date else 0
        
        # Top performing restaurants (time filtered)
        restaurant_filter = Q(order__created_at__date__range=[start_date, end_date]) if start_date else Q()
        top_restaurants = Restaurant.objects.annotate(
            order_count=Count('order', filter=restaurant_filter),
            total_revenue=Sum('order__total_price', filter=restaurant_filter)
        ).order_by('-total_revenue')[:10]
        
        # Order status distribution
        order_statuses = Order.objects.filter(date_filter).values('status').annotate(count=Count('id'))
        
        # Revenue trend data for charts
        revenue_trend = Payment.objects.filter(
            status='success',
            created_at__date__range=[start_date, end_date] if start_date else Q()
        ).extra(
            select={'day': "date(created_at)"}
        ).values('day').annotate(
            daily_revenue=Sum('amount')
        ).order_by('day')
        
        # Additional analytics metrics
        avg_order_value = Order.objects.filter(date_filter).aggregate(Avg('total_price'))['total_price__avg'] or 0
        completed_count = Order.objects.filter(date_filter, status='completed').count()
        completion_rate = (completed_count / total_orders * 100) if total_orders > 0 else 0
        pending_orders = Order.objects.filter(status='pending').count()
        
        # Active carts (SavedCart objects)
        from orders.models import SavedCart
        active_carts = SavedCart.objects.count()
        
        # Today's stats
        today_orders = Order.objects.filter(created_at__date=today).count()
        today_revenue = Payment.objects.filter(status='success', created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        today_new_users = CustomUser.objects.filter(date_joined__date=today).count()
        
        context.update({
            'scope': 'platform',
            'total_restaurants': total_restaurants,
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'new_users': new_users,
            'new_restaurants': new_restaurants,
            'top_restaurants': top_restaurants,
            'order_statuses': order_statuses,
            'revenue_trend': list(revenue_trend),
            'start_date': start_date,
            'end_date': end_date,
            'avg_order_value': avg_order_value,
            'completion_rate': completion_rate,
            'pending_orders': pending_orders,
            'active_carts': active_carts,
            'today_orders': today_orders,
            'today_revenue': today_revenue,
            'today_new_users': today_new_users,
        })
        
    elif user.role == 'restaurant_owner':
        # OWNER ANALYTICS - Enhanced with time filters
        from restaurants.models import Restaurant
        from orders.models import Order
        from payments.models import Payment
        
        # Get owner's restaurants
        restaurants = Restaurant.objects.filter(owner=user)
        restaurant_ids = restaurants.values_list('id', flat=True)
        
        # Base queries with time filter
        date_filter = Q()
        if start_date:
            date_filter = Q(created_at__date__range=[start_date, end_date])
        
        restaurant_filter = Q(restaurant__in=restaurants) & date_filter
        
        # Restaurant metrics
        total_orders = Order.objects.filter(restaurant_filter).count()
        pending_orders = Order.objects.filter(restaurant_filter, status='pending').count()
        completed_orders = Order.objects.filter(restaurant_filter, status='completed').count()
        
        # Revenue analytics
        revenue_filter = Q(order__restaurant__in=restaurants, status='success')
        if start_date:
            revenue_filter &= Q(created_at__date__range=[start_date, end_date])
            
        total_revenue = Payment.objects.filter(revenue_filter).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Popular menu items (time filtered)
        from orders.models import OrderItem
        popular_items = OrderItem.objects.filter(
            order__restaurant__in=restaurants,
            order__created_at__date__range=[start_date, end_date] if start_date else Q()
        ).values(
            'menu_item__name', 'menu_item__category__name'
        ).annotate(
            total_ordered=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_ordered')[:10]
        
        # Order trends for charts
        order_trends = Order.objects.filter(
            restaurant__in=restaurants,
            created_at__date__range=[start_date, end_date] if start_date else Q()
        ).extra(
            select={'day': "date(created_at)"}
        ).values('day').annotate(
            daily_orders=Count('id'),
            daily_revenue=Sum('total_price')
        ).order_by('day')
        
        # Customer metrics
        unique_customers = Order.objects.filter(restaurant_filter).values('customer').distinct().count()
        repeat_customers = Order.objects.filter(
            restaurant__in=restaurants
        ).values('customer').annotate(
            order_count=Count('id')
        ).filter(order_count__gt=1).count()
        
        context.update({
            'scope': 'restaurant',
            'restaurants': restaurants,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
            'popular_items': popular_items,
            'order_trends': list(order_trends),
            'unique_customers': unique_customers,
            'repeat_customers': repeat_customers,
            'start_date': start_date,
            'end_date': end_date,
        })
    
    else:
        # CUSTOMER ANALYTICS - Enhanced
        from orders.models import Order
        
        date_filter = Q()
        if start_date:
            date_filter = Q(created_at__date__range=[start_date, end_date])
            
        customer_orders = Order.objects.filter(Q(customer=user) & date_filter)
        total_orders = customer_orders.count()
        total_spent = customer_orders.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Favorite restaurants
        favorite_restaurants = Order.objects.filter(
            customer=user,
            created_at__date__range=[start_date, end_date] if start_date else Q()
        ).values(
            'restaurant__name'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_price')
        ).order_by('-order_count')[:5]
        
        context.update({
            'scope': 'customer',
            'total_orders': total_orders,
            'total_spent': total_spent,
            'favorite_restaurants': favorite_restaurants,
            'start_date': start_date,
            'end_date': end_date,
        })
    
    return render(request, 'core/analytics_dashboard.html', context)
# ============================================================================
# SETTINGS VIEWS
# ============================================================================

@login_required
def settings_dashboard(request):
    """Settings dashboard - Admin only for platform settings"""
    user = request.user
    
    # Only admin can access platform settings
    if user.role != 'admin' and not user.is_superuser:
        messages.error(request, "Access denied. Admin only.")
        return redirect('dashboard')
    
    from .models import PlatformSettings, PromoCode, AuditLog
    
    # Get or create settings
    settings = PlatformSettings.get_settings()
    
    if request.method == 'POST':
        # Update settings
        settings.site_name = request.POST.get('site_name', settings.site_name)
        settings.site_tagline = request.POST.get('site_tagline', settings.site_tagline)
        settings.support_email = request.POST.get('support_email', settings.support_email)
        settings.support_phone = request.POST.get('support_phone', settings.support_phone)
        
        # Commission & Fees
        settings.commission_percentage = request.POST.get('commission_percentage', settings.commission_percentage)
        settings.minimum_order_amount = request.POST.get('minimum_order_amount', settings.minimum_order_amount)
        settings.delivery_fee = request.POST.get('delivery_fee', settings.delivery_fee)
        settings.free_delivery_threshold = request.POST.get('free_delivery_threshold', settings.free_delivery_threshold)
        
        # Tax Settings
        settings.enable_tax = 'enable_tax' in request.POST
        settings.tax_name = request.POST.get('tax_name', settings.tax_name)
        settings.tax_percentage = request.POST.get('tax_percentage', settings.tax_percentage)
        
        # Payment Settings
        settings.payment_gateway = request.POST.get('payment_gateway', settings.payment_gateway)
        settings.currency = request.POST.get('currency', settings.currency)
        settings.currency_symbol = request.POST.get('currency_symbol', settings.currency_symbol)
        
        # Order Settings
        settings.enable_delivery = 'enable_delivery' in request.POST
        settings.enable_pickup = 'enable_pickup' in request.POST
        settings.enable_dine_in = 'enable_dine_in' in request.POST
        settings.max_order_items = request.POST.get('max_order_items', settings.max_order_items)
        settings.order_timeout_minutes = request.POST.get('order_timeout_minutes', settings.order_timeout_minutes)
        
        # Display Settings
        settings.restaurants_per_page = request.POST.get('restaurants_per_page', settings.restaurants_per_page)
        settings.menu_items_per_page = request.POST.get('menu_items_per_page', settings.menu_items_per_page)
        settings.orders_per_page = request.POST.get('orders_per_page', settings.orders_per_page)
        settings.show_out_of_stock = 'show_out_of_stock' in request.POST
        
        # Feature Toggles (checkboxes)
        settings.allow_guest_checkout = 'allow_guest_checkout' in request.POST
        settings.require_email_verification = 'require_email_verification' in request.POST
        settings.enable_reviews = 'enable_reviews' in request.POST
        settings.enable_promo_codes = 'enable_promo_codes' in request.POST
        settings.auto_approve_restaurants = 'auto_approve_restaurants' in request.POST
        settings.enable_reservations = 'enable_reservations' in request.POST
        
        # Registration Controls
        settings.allow_customer_registration = 'allow_customer_registration' in request.POST
        settings.allow_restaurant_registration = 'allow_restaurant_registration' in request.POST
        
        # Notification Settings
        settings.enable_notifications = 'enable_notifications' in request.POST
        settings.enable_sms_notifications = 'enable_sms_notifications' in request.POST
        
        # Maintenance Mode
        settings.maintenance_mode = 'maintenance_mode' in request.POST
        settings.maintenance_message = request.POST.get('maintenance_message', settings.maintenance_message)
        
        settings.updated_by = user
        settings.save()
        
        # Log the action
        AuditLog.log(
            user=user,
            action_type='settings_update',
            description='Platform settings updated',
            target_model='PlatformSettings',
            target_id=1,
            request=request
        )
        
        messages.success(request, 'Platform settings saved successfully!')
        return redirect('settings_dashboard')
    
    # Stats for sidebar
    total_commission = Order.objects.filter(status='completed').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    total_commission = float(total_commission) * float(settings.commission_percentage) / 100
    
    active_promos = PromoCode.objects.filter(is_active=True).count()
    total_promo_usage = PromoCode.objects.aggregate(total=Sum('usage_count'))['total'] or 0
    audit_log_count = AuditLog.objects.count()
    
    context = {
        'user': user,
        'settings': settings,
        'total_commission': total_commission,
        'active_promos': active_promos,
        'total_promo_usage': total_promo_usage,
        'audit_log_count': audit_log_count,
    }
    
    return render(request, 'core/settings_dashboard.html', context)

# ============================================================================
# NOTIFICATIONS VIEWS  
# ============================================================================

@login_required
def notifications_dashboard(request):
    """Notifications dashboard based on user role"""
    user = request.user
    context = {'user': user}
    
    if user.role == 'admin':
        # ADMIN NOTIFICATIONS - Platform alerts
        from orders.models import Order, SavedCart
        from restaurants.models import Restaurant
        from datetime import timedelta
        
        # Pending orders across platform
        pending_orders = Order.objects.filter(status='pending').select_related('restaurant', 'customer').order_by('-created_at')
        
        # Active carts
        active_carts = SavedCart.objects.select_related('customer', 'restaurant').prefetch_related('items__menu_item').order_by('-updated_at')
        
        # Today's activity
        today_orders = Order.objects.filter(created_at__date=timezone.now().date()).select_related('restaurant', 'customer').order_by('-created_at')
        
        # Recent restaurants (this week)
        week_ago = timezone.now() - timedelta(days=7)
        new_restaurants = Restaurant.objects.filter(created_at__gte=week_ago).select_related('owner').order_by('-created_at')
        
        # All recent orders
        all_orders = Order.objects.select_related('restaurant', 'customer').order_by('-created_at')[:50]
        
        context.update({
            'scope': 'platform',
            'pending_orders': pending_orders,
            'active_carts': active_carts,
            'today_orders': today_orders,
            'new_restaurants': new_restaurants,
            'all_orders': all_orders,
            'pending_count': pending_orders.count(),
            'carts_count': active_carts.count(),
            'today_count': today_orders.count(),
        })
        
    elif user.role == 'restaurant_owner':
        # OWNER NOTIFICATIONS - Restaurant alerts
        from orders.models import Order, SavedCart
        from restaurants.models import Restaurant
        
        restaurants = Restaurant.objects.filter(owner=user)
        
        # Pending orders for owner's restaurants
        pending_orders = Order.objects.filter(
            restaurant__in=restaurants,
            status='pending'
        ).select_related('restaurant', 'customer').order_by('-created_at')
        
        # Active carts for owner's restaurants
        active_carts = SavedCart.objects.filter(
            restaurant__in=restaurants
        ).select_related('customer', 'restaurant').prefetch_related('items__menu_item').order_by('-updated_at')
        
        # Today's orders
        today_orders = Order.objects.filter(
            restaurant__in=restaurants,
            created_at__date=timezone.now().date()
        ).select_related('restaurant', 'customer').order_by('-created_at')
        
        # All recent orders
        all_orders = Order.objects.filter(
            restaurant__in=restaurants
        ).select_related('restaurant', 'customer').order_by('-created_at')[:50]
        
        context.update({
            'scope': 'restaurant',
            'restaurants': restaurants,
            'pending_orders': pending_orders,
            'active_carts': active_carts,
            'today_orders': today_orders,
            'all_orders': all_orders,
            'pending_count': pending_orders.count(),
            'carts_count': active_carts.count(),
            'today_count': today_orders.count(),
        })
    
    else:
        # CUSTOMER NOTIFICATIONS - Personal notifications
        from orders.models import Order
        
        # Active orders (not completed/cancelled)
        active_orders = Order.objects.filter(
            customer=user
        ).exclude(status__in=['completed', 'cancelled']).select_related('restaurant').order_by('-created_at')
        
        # All orders
        all_orders = Order.objects.filter(customer=user).select_related('restaurant').order_by('-created_at')[:20]
        
        # Cart items from session
        cart = request.session.get('cart', {})
        cart_items = []
        if cart and 'items' in cart:
            cart_items = cart['items']
        
        context.update({
            'scope': 'customer',
            'active_orders': active_orders,
            'all_orders': all_orders,
            'cart_items': cart_items,
            'active_count': active_orders.count(),
            'cart_count': len(cart_items),
        })
    
    return render(request, 'core/notifications_dashboard.html', context)


# ============== ADMIN MANAGEMENT VIEWS ==============

@login_required
def admin_toggle_user(request, user_id):
    """Toggle user active status (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent admin from deactivating themselves
        if target_user == request.user:
            messages.error(request, "You cannot deactivate yourself.")
            return redirect('dashboard')
        
        target_user.is_active = not target_user.is_active
        target_user.save()
        
        status = 'activated' if target_user.is_active else 'deactivated'
        
        AuditLog.log(
            user=request.user,
            action_type='user_toggle',
            description=f'User {target_user.username} {status}',
            target_model='CustomUser',
            target_id=target_user.id,
            request=request
        )
        
        messages.success(request, f'User "{target_user.username}" has been {status}.')
    
    return redirect('dashboard')


@login_required
def admin_change_user_role(request, user_id):
    """Change user role (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        new_role = request.POST.get('role')
        
        # Prevent admin from changing their own role
        if target_user == request.user:
            messages.error(request, "You cannot change your own role.")
            return redirect('dashboard')
        
        valid_roles = ['admin', 'restaurant_owner', 'customer']
        if new_role in valid_roles:
            old_role = target_user.role
            target_user.role = new_role
            target_user.save()
            
            AuditLog.log(
                user=request.user,
                action_type='user_role_change',
                description=f'User {target_user.username} role changed from {old_role} to {new_role}',
                target_model='CustomUser',
                target_id=target_user.id,
                request=request,
                extra_data={'old_role': old_role, 'new_role': new_role}
            )
            
            messages.success(request, f'User "{target_user.username}" role changed from {old_role} to {new_role}.')
        else:
            messages.error(request, 'Invalid role specified.')
    
    return redirect('dashboard')


@login_required
def admin_delete_user(request, user_id):
    """Delete user account (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent admin from deleting themselves
        if target_user == request.user:
            messages.error(request, "You cannot delete yourself.")
            return redirect('dashboard')
        
        username = target_user.username
        user_id_deleted = target_user.id
        target_user.delete()
        
        AuditLog.log(
            user=request.user,
            action_type='user_delete',
            description=f'User {username} (ID: {user_id_deleted}) deleted',
            target_model='CustomUser',
            request=request
        )
        
        messages.success(request, f'User "{username}" has been deleted.')
    
    return redirect('dashboard')


@login_required
def admin_toggle_restaurant(request, restaurant_id):
    """Toggle restaurant active status (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    if request.method == 'POST':
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant.is_active = not restaurant.is_active
        restaurant.save()
        
        status = 'activated' if restaurant.is_active else 'suspended'
        
        AuditLog.log(
            user=request.user,
            action_type='restaurant_toggle',
            description=f'Restaurant {restaurant.name} {status}',
            target_model='Restaurant',
            target_id=restaurant.id,
            request=request
        )
        
        messages.success(request, f'Restaurant "{restaurant.name}" has been {status}.')
    
    return redirect('dashboard')


@login_required
def admin_delete_restaurant(request, restaurant_id):
    """Delete restaurant (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    if request.method == 'POST':
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        name = restaurant.name
        rest_id = restaurant.id
        restaurant.delete()
        
        AuditLog.log(
            user=request.user,
            action_type='restaurant_delete',
            description=f'Restaurant {name} (ID: {rest_id}) deleted permanently',
            target_model='Restaurant',
            request=request
        )
        
        messages.success(request, f'Restaurant "{name}" has been deleted permanently.')
    
    return redirect('dashboard')


# ============================================================================
# PROMO CODE MANAGEMENT VIEWS
# ============================================================================

@login_required
def promo_code_list(request):
    """List all promo codes (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import PromoCode
    
    promos = PromoCode.objects.all().order_by('-created_at')
    
    # Stats
    active_count = promos.filter(is_active=True).count()
    total_usage = sum(p.usage_count for p in promos)
    
    context = {
        'promos': promos,
        'active_count': active_count,
        'total_count': promos.count(),
        'total_usage': total_usage,
    }
    return render(request, 'core/promo_codes.html', context)


@login_required
def promo_code_create(request):
    """Create new promo code (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import PromoCode, AuditLog
    
    if request.method == 'POST':
        try:
            code = request.POST.get('code', '').upper().strip()
            
            # Check if code already exists
            if PromoCode.objects.filter(code=code).exists():
                messages.error(request, f'Promo code "{code}" already exists.')
                return redirect('promo_code_list')
            
            promo = PromoCode.objects.create(
                code=code,
                description=request.POST.get('description', ''),
                discount_type=request.POST.get('discount_type', 'percentage'),
                discount_value=request.POST.get('discount_value', 10),
                minimum_order=request.POST.get('minimum_order', 0),
                maximum_discount=request.POST.get('maximum_discount') or None,
                usage_limit=request.POST.get('usage_limit', 0),
                per_user_limit=request.POST.get('per_user_limit', 1),
                is_active='is_active' in request.POST,
                first_order_only='first_order_only' in request.POST,
                created_by=request.user,
            )
            
            # Handle valid_until date
            valid_until = request.POST.get('valid_until')
            if valid_until:
                promo.valid_until = valid_until
                promo.save()
            
            # Log the action
            AuditLog.log(
                user=request.user,
                action_type='promo_create',
                description=f'Created promo code: {code}',
                target_model='PromoCode',
                target_id=promo.id,
                request=request
            )
            
            messages.success(request, f'Promo code "{code}" created successfully!')
            
        except Exception as e:
            messages.error(request, f'Error creating promo code: {str(e)}')
    
    return redirect('promo_code_list')


@login_required
def promo_code_toggle(request, promo_id):
    """Toggle promo code active status (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import PromoCode, AuditLog
    
    if request.method == 'POST':
        promo = get_object_or_404(PromoCode, id=promo_id)
        promo.is_active = not promo.is_active
        promo.save()
        
        status = 'activated' if promo.is_active else 'deactivated'
        
        AuditLog.log(
            user=request.user,
            action_type='promo_update',
            description=f'Promo code {promo.code} {status}',
            target_model='PromoCode',
            target_id=promo.id,
            request=request
        )
        
        messages.success(request, f'Promo code "{promo.code}" has been {status}.')
    
    return redirect('promo_code_list')


@login_required
def promo_code_delete(request, promo_id):
    """Delete promo code (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import PromoCode, AuditLog
    
    if request.method == 'POST':
        promo = get_object_or_404(PromoCode, id=promo_id)
        code = promo.code
        promo.delete()
        
        AuditLog.log(
            user=request.user,
            action_type='promo_delete',
            description=f'Deleted promo code: {code}',
            target_model='PromoCode',
            request=request
        )
        
        messages.success(request, f'Promo code "{code}" has been deleted.')
    
    return redirect('promo_code_list')


# ============================================================================
# EXPORT FUNCTIONALITY VIEWS
# ============================================================================

@login_required
def export_users(request):
    """Export users to CSV (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Role', 'Phone', 'Is Active', 'Is Verified', 'Date Joined', 'Last Login'])
    
    users = CustomUser.objects.all().order_by('-date_joined')
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.role,
            user.phone_number or '',
            'Yes' if user.is_active else 'No',
            'Yes' if user.is_verified else 'No',
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
        ])
    
    AuditLog.log(
        user=request.user,
        action_type='export_data',
        description=f'Exported {users.count()} users to CSV',
        target_model='CustomUser',
        request=request
    )
    
    return response


@login_required
def export_restaurants(request):
    """Export restaurants to CSV (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="restaurants_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Owner', 'Owner Email', 'Address', 'Phone', 'Is Active', 'Total Orders', 'Total Revenue', 'Created At'])
    
    restaurants = Restaurant.objects.select_related('owner').all()
    for r in restaurants:
        order_count = Order.objects.filter(restaurant=r).count()
        revenue = Order.objects.filter(restaurant=r, status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        writer.writerow([
            r.id,
            r.name,
            r.owner.username,
            r.owner.email,
            r.address,
            r.phone,
            'Yes' if r.is_active else 'No',
            order_count,
            f'{revenue:.2f}',
            r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    AuditLog.log(
        user=request.user,
        action_type='export_data',
        description=f'Exported {restaurants.count()} restaurants to CSV',
        target_model='Restaurant',
        request=request
    )
    
    return response


@login_required
def export_orders(request):
    """Export orders to CSV (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog, PlatformSettings
    
    settings = PlatformSettings.get_settings()
    commission_rate = float(settings.commission_percentage)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Restaurant', 'Customer', 'Customer Email', 'Status', 'Total', 'Commission', 'Restaurant Earns', 'Created At'])
    
    orders = Order.objects.select_related('restaurant', 'customer').all().order_by('-created_at')
    for order in orders:
        commission = float(order.total_price) * commission_rate / 100
        restaurant_earns = float(order.total_price) - commission
        
        writer.writerow([
            order.id,
            order.restaurant.name,
            order.customer.username,
            order.customer_email,
            order.status,
            f'{order.total_price:.2f}',
            f'{commission:.2f}',
            f'{restaurant_earns:.2f}',
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    AuditLog.log(
        user=request.user,
        action_type='export_data',
        description=f'Exported {orders.count()} orders to CSV',
        target_model='Order',
        request=request
    )
    
    return response


@login_required
def export_revenue_report(request):
    """Export revenue report to CSV (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog, PlatformSettings
    
    settings = PlatformSettings.get_settings()
    commission_rate = float(settings.commission_percentage)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="revenue_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Summary section
    writer.writerow(['=== REVENUE REPORT ==='])
    writer.writerow(['Generated:', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Commission Rate:', f'{commission_rate}%'])
    writer.writerow([])
    
    # Overall stats
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status='completed').count()
    total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_commission = float(total_revenue) * commission_rate / 100
    
    writer.writerow(['=== SUMMARY ==='])
    writer.writerow(['Total Orders:', total_orders])
    writer.writerow(['Completed Orders:', completed_orders])
    writer.writerow(['Total Revenue:', f'{total_revenue:.2f}'])
    writer.writerow(['Platform Commission:', f'{total_commission:.2f}'])
    writer.writerow(['Restaurant Payouts:', f'{float(total_revenue) - total_commission:.2f}'])
    writer.writerow([])
    
    # Revenue by restaurant
    writer.writerow(['=== REVENUE BY RESTAURANT ==='])
    writer.writerow(['Restaurant', 'Owner', 'Total Orders', 'Completed Orders', 'Gross Revenue', 'Platform Commission', 'Net Payout'])
    
    restaurants = Restaurant.objects.select_related('owner').all()
    for r in restaurants:
        r_orders = Order.objects.filter(restaurant=r)
        r_total = r_orders.count()
        r_completed = r_orders.filter(status='completed').count()
        r_revenue = r_orders.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        r_commission = float(r_revenue) * commission_rate / 100
        
        writer.writerow([
            r.name,
            r.owner.username,
            r_total,
            r_completed,
            f'{r_revenue:.2f}',
            f'{r_commission:.2f}',
            f'{float(r_revenue) - r_commission:.2f}',
        ])
    
    AuditLog.log(
        user=request.user,
        action_type='export_data',
        description='Exported revenue report to CSV',
        target_model='Payment',
        request=request
    )
    
    return response


# ============================================================================
# AUDIT LOG VIEWS
# ============================================================================

@login_required
def audit_log_list(request):
    """View audit logs (Admin only)"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import AuditLog
    
    logs = AuditLog.objects.select_related('user').all().order_by('-created_at')
    
    # Filter by action type
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    # Filter by user
    user_filter = request.GET.get('user_id')
    if user_filter:
        logs = logs.filter(user_id=user_filter)
    
    # Filter by date
    date_filter = request.GET.get('date')
    if date_filter:
        logs = logs.filter(created_at__date=date_filter)
    
    # Limit to last 500
    logs = logs[:500]
    
    # Get unique action types for filter dropdown
    action_types = AuditLog.ACTION_TYPES
    
    # Get admin users for filter
    admin_users = CustomUser.objects.filter(role='admin')
    
    context = {
        'logs': logs,
        'action_types': action_types,
        'admin_users': admin_users,
        'current_action': action_filter,
        'current_user_id': user_filter,
        'current_date': date_filter,
    }
    return render(request, 'core/audit_logs.html', context)


# ============================================================================
# VALIDATE PROMO CODE (API for checkout)
# ============================================================================

@login_required
def validate_promo_code(request):
    """Validate a promo code via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'valid': False, 'error': 'Invalid request method'})
    
    from .models import PromoCode, PromoCodeUsage, PlatformSettings
    
    settings = PlatformSettings.get_settings()
    if not settings.enable_promo_codes:
        return JsonResponse({'valid': False, 'error': 'Promo codes are currently disabled'})
    
    code = request.POST.get('code', '').upper().strip()
    order_total = float(request.POST.get('order_total', 0))
    restaurant_id = request.POST.get('restaurant_id')
    
    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Invalid promo code'})
    
    # Check validity
    is_valid, message = promo.is_valid()
    if not is_valid:
        return JsonResponse({'valid': False, 'error': message})
    
    # Check minimum order
    if order_total < float(promo.minimum_order):
        return JsonResponse({
            'valid': False, 
            'error': f'Minimum order amount of ₦{promo.minimum_order} required'
        })
    
    # Check per-user limit
    user_usage = PromoCodeUsage.objects.filter(promo_code=promo, user=request.user).count()
    if user_usage >= promo.per_user_limit:
        return JsonResponse({'valid': False, 'error': 'You have already used this promo code'})
    
    # Check first order only
    if promo.first_order_only:
        user_orders = Order.objects.filter(customer=request.user, status='completed').count()
        if user_orders > 0:
            return JsonResponse({'valid': False, 'error': 'This promo code is only valid for first orders'})
    
    # Check restaurant restriction
    if not promo.all_restaurants and restaurant_id:
        if not promo.restaurants.filter(id=restaurant_id).exists():
            return JsonResponse({'valid': False, 'error': 'This promo code is not valid for this restaurant'})
    
    # Calculate discount
    discount = promo.calculate_discount(order_total)
    
    return JsonResponse({
        'valid': True,
        'discount': float(discount),
        'discount_display': promo.get_discount_display(),
        'code': promo.code,
        'new_total': order_total - float(discount),
    })