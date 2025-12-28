from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Restaurant, Category, MenuItem, GalleryImage, Staff, StaffInvite
from orders.models import Order
from payments.models import Payment
from reviews.models import Feedback

User = get_user_model()


# PUBLIC VIEW - Restaurant detail page
def restaurant_detail(request, slug):
    """Public restaurant detail page with menu"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
        categories = Category.objects.filter(restaurant=restaurant).prefetch_related('menuitem_set')

        # Check if this is user's preferred restaurant
        is_preferred = False
        if request.user.is_authenticated and getattr(request.user, 'role', None) == 'customer':
            is_preferred = getattr(request.user, 'preferred_restaurant', None) == restaurant

        # If the viewer is the customer, include their past orders/payments for this restaurant
        user_orders = None
        user_payments = None
        if request.user.is_authenticated and getattr(request.user, 'role', None) == 'customer':
            try:
                user_orders = Order.objects.filter(customer=request.user, restaurant=restaurant).order_by('-created_at')[:5]
            except Exception as e:
                logger.error(f"Error fetching user orders: {e}")
                user_orders = None
            try:
                user_payments = Payment.objects.filter(order__customer=request.user, order__restaurant=restaurant).order_by('-created_at')[:5]
            except Exception as e:
                logger.error(f"Error fetching user payments: {e}")
                user_payments = None

        # Recent public feedback for this restaurant
        try:
            recent_feedback = Feedback.objects.filter(restaurant=restaurant, is_public=True).order_by('-created_at')[:5]
        except Exception as e:
            logger.error(f"Error fetching feedback: {e}")
            recent_feedback = None

        context = {
            'restaurant': restaurant,
            'categories': categories,
            'is_preferred': is_preferred,
            'user_orders': user_orders,
            'user_payments': user_payments,
            'recent_feedback': recent_feedback,
        }
        return render(request, 'restaurants/restaurant_detail.html', context)
    except Exception as e:
        logger.exception(f"Error in restaurant_detail view for slug '{slug}': {e}")
        return render(request, 'restaurants/restaurant_detail.html', {
            'restaurant': None,
            'categories': [],
            'is_preferred': False,
            'user_orders': None,
            'user_payments': None,
            'recent_feedback': None,
            'error_message': f"An error occurred: {e}"
        })

@login_required
def set_preferred_restaurant(request, slug):
    """Set a restaurant as customer's preferred/default restaurant"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can set preferred restaurants.')
        return redirect('restaurant_detail', slug=slug)
    
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    request.user.preferred_restaurant = restaurant
    request.user.save()
    
    messages.success(request, f'{restaurant.name} is now your default restaurant! You can access it directly anytime.')
    return redirect('restaurant_detail', slug=slug)

@login_required
def remove_preferred_restaurant(request):
    """Remove preferred restaurant setting"""
    if request.user.role != 'customer':
        messages.error(request, 'Invalid action.')
        return redirect('dashboard')
    
    request.user.preferred_restaurant = None
    request.user.save()
    
    messages.success(request, 'Preferred restaurant removed. You can now browse all restaurants.')
    return redirect('browse_restaurants')

# RESTAURANT OWNER VIEWS
@login_required
def restaurant_dashboard(request):
    # Clear loader session flag if requested
    if request.method == 'GET' and request.GET.get('clear_loader') == '1':
        if 'show_loader_after_login' in request.session:
            del request.session['show_loader_after_login']
    """Restaurant owner dashboard"""
    if request.user.role != 'restaurant_owner':
        messages.error(request, 'Access denied. Restaurant owners only.')
        return redirect('dashboard')
    
    restaurants = Restaurant.objects.filter(owner=request.user)
    recent_orders = Order.objects.filter(restaurant__owner=request.user).order_by('-created_at')[:10]
    
    # Basic stats
    total_orders = Order.objects.filter(restaurant__owner=request.user).count()
    pending_orders = Order.objects.filter(restaurant__owner=request.user, status='pending').count()
    completed_orders = Order.objects.filter(restaurant__owner=request.user, status__in=['confirmed', 'completed']).count()
    
    # Revenue calculation
    from django.db.models import Sum
    total_revenue = Order.objects.filter(
        restaurant__owner=request.user, 
        status__in=['confirmed', 'completed']
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Today's stats
    from django.utils import timezone
    today = timezone.now().date()
    today_orders = Order.objects.filter(
        restaurant__owner=request.user,
        created_at__date=today
    ).count()
    today_revenue = Order.objects.filter(
        restaurant__owner=request.user,
        status__in=['confirmed', 'completed'],
        created_at__date=today
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # This month's stats
    from datetime import timedelta
    first_day_of_month = today.replace(day=1)
    monthly_revenue = Order.objects.filter(
        restaurant__owner=request.user,
        status__in=['confirmed', 'completed'],
        created_at__date__gte=first_day_of_month
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    monthly_orders = Order.objects.filter(
        restaurant__owner=request.user,
        created_at__date__gte=first_day_of_month
    ).count()
    
    # Active orders (not completed/cancelled)
    active_orders = Order.objects.filter(
        restaurant__owner=request.user,
        status__in=['pending', 'awaiting_confirmation', 'preparing', 'ready']
    ).order_by('-created_at')[:5]
    
    # Menu items count
    from restaurants.models import MenuItem
    total_menu_items = MenuItem.objects.filter(category__restaurant__owner=request.user).count()
    
    # Staff count
    total_staff = Staff.objects.filter(restaurant__owner=request.user, is_active=True).count()
    
    context = {
        'restaurants': restaurants,
        'recent_orders': recent_orders,
        'active_orders': active_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'monthly_revenue': monthly_revenue,
        'monthly_orders': monthly_orders,
        'total_menu_items': total_menu_items,
        'total_staff': total_staff,
    }
    return render(request, 'restaurants/restaurant_dashboard.html', context)

@login_required
def manage_restaurant(request, restaurant_id=None):
    """Create or edit restaurant"""
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    # Only restaurant owners and admins can access
    if user.role != 'restaurant_owner' and not is_admin:
        messages.error(request, 'Access denied. Restaurant owners only.')
        return redirect('dashboard')
    
    if restaurant_id:
        # Admins can edit any restaurant, owners can only edit their own
        if is_admin:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    else:
        restaurant = None
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        opening_time = request.POST.get('opening_time')
        closing_time = request.POST.get('closing_time')
        
        if restaurant:
            # Update existing restaurant
            restaurant.name = name
            restaurant.description = description
            restaurant.address = address
            restaurant.phone = phone
            restaurant.email = email
            restaurant.opening_time = opening_time
            restaurant.closing_time = closing_time
            
            # Payment methods
            restaurant.accepts_cash = request.POST.get('accepts_cash') == 'on'
            restaurant.accepts_card = request.POST.get('accepts_card') == 'on'
            restaurant.accepts_bank_transfer = request.POST.get('accepts_bank_transfer') == 'on'
            restaurant.accepts_mobile_money = request.POST.get('accepts_mobile_money') == 'on'
            restaurant.accepts_paystack = request.POST.get('accepts_paystack') == 'on'
            restaurant.accepts_pos = request.POST.get('accepts_pos') == 'on'
            restaurant.bank_name = request.POST.get('bank_name', '')
            restaurant.bank_account_number = request.POST.get('bank_account_number', '')
            restaurant.bank_account_name = request.POST.get('bank_account_name', '')
            restaurant.mobile_money_provider = request.POST.get('mobile_money_provider', '')
            restaurant.mobile_money_number = request.POST.get('mobile_money_number', '')
            
            # Theme & Appearance Settings
            restaurant.template_style = request.POST.get('template_style', 'classic')
            restaurant.font_style = request.POST.get('font_style', 'default')
            restaurant.header_style = request.POST.get('header_style', 'full_banner')
            restaurant.menu_layout = request.POST.get('menu_layout', 'grid')
            restaurant.button_style = request.POST.get('button_style', 'rounded')
            
            # Colors
            restaurant.primary_color = request.POST.get('primary_color', '#007bff')
            restaurant.secondary_color = request.POST.get('secondary_color', '#6c757d')
            restaurant.accent_color = request.POST.get('accent_color', '#28a745')
            restaurant.text_color = request.POST.get('text_color', '#333333')
            restaurant.background_color = request.POST.get('background_color', '#ffffff')
            restaurant.header_bg_color = request.POST.get('header_bg_color', '#000000')
            restaurant.header_text_color = request.POST.get('header_text_color', '#ffffff')
            
            # Section Visibility
            restaurant.show_hero = request.POST.get('show_hero') == 'on'
            restaurant.show_about = request.POST.get('show_about') == 'on'
            restaurant.show_gallery = request.POST.get('show_gallery') == 'on'
            restaurant.show_reviews = request.POST.get('show_reviews') == 'on'
            restaurant.show_contact = request.POST.get('show_contact') == 'on'
            restaurant.show_social = request.POST.get('show_social') == 'on'
            restaurant.show_chef = request.POST.get('show_chef') == 'on'
            restaurant.show_hours = request.POST.get('show_hours') == 'on'
            
            # Custom CSS
            restaurant.custom_css = request.POST.get('custom_css', '')
            
            # Handle logo upload
            if 'logo' in request.FILES:
                restaurant.logo = request.FILES['logo']
            elif request.POST.get('remove_logo'):
                restaurant.logo = None
            
            # Handle banner image upload
            if 'banner_image' in request.FILES:
                restaurant.banner_image = request.FILES['banner_image']
            elif request.POST.get('remove_banner'):
                restaurant.banner_image = None
            
            # Handle header video upload
            if 'header_video' in request.FILES:
                restaurant.header_video = request.FILES['header_video']
            elif request.POST.get('remove_video'):
                restaurant.header_video = None
            
            restaurant.save()
            
            # Handle gallery image updates (captions and removals)
            for key in request.POST:
                if key.startswith('gallery_caption_'):
                    gallery_id = key.replace('gallery_caption_', '')
                    try:
                        gallery_img = GalleryImage.objects.get(id=gallery_id, restaurant=restaurant)
                        gallery_img.caption = request.POST.get(key)
                        gallery_img.save()
                    except GalleryImage.DoesNotExist:
                        pass
                
                if key.startswith('remove_gallery_'):
                    gallery_id = key.replace('remove_gallery_', '')
                    try:
                        gallery_img = GalleryImage.objects.get(id=gallery_id, restaurant=restaurant)
                        gallery_img.delete()
                    except GalleryImage.DoesNotExist:
                        pass
            
            # Handle new gallery images
            if 'gallery_images' in request.FILES:
                gallery_files = request.FILES.getlist('gallery_images')
                for gallery_file in gallery_files:
                    GalleryImage.objects.create(
                        restaurant=restaurant,
                        image=gallery_file
                    )
            
            messages.success(request, 'Restaurant updated successfully!')
        else:
            # Create new restaurant
            restaurant = Restaurant.objects.create(
                owner=request.user,
                name=name,
                description=description,
                address=address,
                phone=phone,
                email=email,
                opening_time=opening_time,
                closing_time=closing_time,
                slug=name.lower().replace(' ', '-'),
                # Payment methods
                accepts_cash=request.POST.get('accepts_cash') == 'on',
                accepts_card=request.POST.get('accepts_card') == 'on',
                accepts_bank_transfer=request.POST.get('accepts_bank_transfer') == 'on',
                accepts_mobile_money=request.POST.get('accepts_mobile_money') == 'on',
                accepts_paystack=request.POST.get('accepts_paystack') == 'on',
                accepts_pos=request.POST.get('accepts_pos') == 'on',
                bank_name=request.POST.get('bank_name', ''),
                bank_account_number=request.POST.get('bank_account_number', ''),
                bank_account_name=request.POST.get('bank_account_name', ''),
                mobile_money_provider=request.POST.get('mobile_money_provider', ''),
                mobile_money_number=request.POST.get('mobile_money_number', ''),
                # Theme & Appearance Settings
                template_style=request.POST.get('template_style', 'classic'),
                font_style=request.POST.get('font_style', 'default'),
                header_style=request.POST.get('header_style', 'full_banner'),
                menu_layout=request.POST.get('menu_layout', 'grid'),
                button_style=request.POST.get('button_style', 'rounded'),
                # Colors
                primary_color=request.POST.get('primary_color', '#007bff'),
                secondary_color=request.POST.get('secondary_color', '#6c757d'),
                accent_color=request.POST.get('accent_color', '#28a745'),
                text_color=request.POST.get('text_color', '#333333'),
                background_color=request.POST.get('background_color', '#ffffff'),
                header_bg_color=request.POST.get('header_bg_color', '#000000'),
                header_text_color=request.POST.get('header_text_color', '#ffffff'),
                # Section Visibility
                show_hero=request.POST.get('show_hero') == 'on',
                show_about=request.POST.get('show_about') == 'on',
                show_gallery=request.POST.get('show_gallery') == 'on',
                show_reviews=request.POST.get('show_reviews') == 'on',
                show_contact=request.POST.get('show_contact') == 'on',
                show_social=request.POST.get('show_social') == 'on',
                show_chef=request.POST.get('show_chef') == 'on',
                show_hours=request.POST.get('show_hours') == 'on',
                # Custom CSS
                custom_css=request.POST.get('custom_css', '')
            )
            
            # Handle logo upload for new restaurant
            if 'logo' in request.FILES:
                restaurant.logo = request.FILES['logo']
            
            # Handle banner image upload for new restaurant
            if 'banner_image' in request.FILES:
                restaurant.banner_image = request.FILES['banner_image']
            
            restaurant.save()
            
            # Handle gallery images for new restaurant
            if 'gallery_images' in request.FILES:
                gallery_files = request.FILES.getlist('gallery_images')
                for gallery_file in gallery_files:
                    GalleryImage.objects.create(
                        restaurant=restaurant,
                        image=gallery_file
                    )
            
            messages.success(request, 'Restaurant created successfully!')
        
        return redirect('restaurant_dashboard')
    
    context = {
        'restaurant': restaurant,
        # Theme choices for the customizer
        'template_choices': Restaurant.TEMPLATE_CHOICES,
        'font_choices': Restaurant.FONT_CHOICES,
        'header_choices': Restaurant.HEADER_CHOICES,
        'menu_layout_choices': Restaurant.MENU_LAYOUT_CHOICES,
        'button_choices': Restaurant.BUTTON_STYLE_CHOICES,
    }
    return render(request, 'restaurants/manage_restaurant.html', context)

@login_required
def manage_menu(request, restaurant_id):
    """Manage restaurant menu categories and items"""
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    if user.role != 'restaurant_owner' and not is_admin:
        messages.error(request, 'Access denied. Restaurant owners only.')
        return redirect('dashboard')
    
    # Admins can access any restaurant, owners only their own
    if is_admin:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    else:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    categories = Category.objects.filter(restaurant=restaurant)
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
    }
    return render(request, 'restaurants/manage_menu.html', context)

@login_required
def add_category(request, restaurant_id):
    """Add new category"""
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    if user.role != 'restaurant_owner' and not is_admin:
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    if request.method == 'POST':
        if is_admin:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        category = Category.objects.create(
            restaurant=restaurant,
            name=name,
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Category added successfully!',
            'category_id': category.id
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def add_menu_item(request, restaurant_id, category_id):
    """Add new menu item"""
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    if user.role != 'restaurant_owner' and not is_admin:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        if is_admin:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
        category = get_object_or_404(Category, id=category_id, restaurant=restaurant)
        
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        preparation_time = request.POST.get('preparation_time', 15)
        image = request.FILES.get('image')  # Get uploaded image
        
        menu_item = MenuItem.objects.create(
            category=category,
            name=name,
            description=description,
            price=price,
            preparation_time=preparation_time,
            image=image  # Save the image
        )
        
        messages.success(request, f'{name} added successfully!')
        return redirect('manage_menu', restaurant_id=restaurant_id)
    
    return redirect('manage_menu', restaurant_id=restaurant_id)

@login_required
def toggle_menu_item(request, item_id):
    """Toggle menu item availability with enhanced options"""
    from django.utils import timezone
    
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    if user.role != 'restaurant_owner' and not is_admin:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        if is_admin:
            menu_item = get_object_or_404(MenuItem, id=item_id)
        else:
            menu_item = get_object_or_404(MenuItem, id=item_id, category__restaurant__owner=request.user)
        
        action = request.POST.get('toggle_action', 'toggle')
        
        if action == 'disable':
            # Disabling the item
            menu_item.is_available = False
            reason = request.POST.get('disable_reason', '')
            custom_reason = request.POST.get('custom_reason', '')
            
            # Save the reason
            menu_item.disabled_reason = reason if reason else ''
            menu_item.disabled_reason_note = custom_reason if reason == 'other' else ''
            menu_item.disabled_at = timezone.now()
            
            # Get display text for message
            reason_text = custom_reason if reason == 'other' else dict([
                ('sold_out', 'Sold Out'),
                ('seasonal', 'Seasonal Item'),
                ('ingredients', 'Missing Ingredients'),
                ('maintenance', 'Under Maintenance'),
                ('discontinued', 'Discontinued'),
                ('', 'No reason provided')
            ]).get(reason, reason)
            
            menu_item.save()
            messages.warning(request, f'"{menu_item.name}" has been disabled. Reason: {reason_text}')
            
        elif action == 'enable':
            # Enabling the item
            menu_item.is_available = True
            menu_item.disabled_reason = ''
            menu_item.disabled_reason_note = ''
            menu_item.disabled_at = None
            
            # If stock tracking is enabled, update stock quantity
            if menu_item.track_stock:
                stock_qty = int(request.POST.get('stock_quantity', 0))
                if stock_qty > 0:
                    menu_item.stock_quantity = stock_qty
                    messages.success(request, f'"{menu_item.name}" has been enabled with {stock_qty} in stock.')
                else:
                    messages.success(request, f'"{menu_item.name}" has been enabled.')
            else:
                messages.success(request, f'"{menu_item.name}" is now available for ordering.')
            
            menu_item.save()
        else:
            # Simple toggle (fallback)
            menu_item.is_available = not menu_item.is_available
            if not menu_item.is_available:
                menu_item.disabled_at = timezone.now()
            else:
                menu_item.disabled_reason = ''
                menu_item.disabled_reason_note = ''
                menu_item.disabled_at = None
            menu_item.save()
            status = 'enabled' if menu_item.is_available else 'disabled'
            messages.info(request, f'"{menu_item.name}" has been {status}.')
        
        return redirect('manage_menu', restaurant_id=menu_item.category.restaurant.id)
    
    messages.error(request, 'Invalid request')
    return redirect('dashboard')

@login_required
def update_stock(request, item_id):
    """Update menu item stock quantity"""
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    if user.role != 'restaurant_owner' and not is_admin:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        if is_admin:
            menu_item = get_object_or_404(MenuItem, id=item_id)
        else:
            menu_item = get_object_or_404(MenuItem, id=item_id, category__restaurant__owner=request.user)
        
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 0))
        
        if action == 'add':
            menu_item.stock_quantity += quantity
            messages.success(request, f'Added {quantity} to {menu_item.name} stock. New total: {menu_item.stock_quantity}')
        elif action == 'set':
            menu_item.stock_quantity = quantity
            messages.success(request, f'Set {menu_item.name} stock to {quantity}')
        
        # Auto-enable if stock added to out-of-stock item
        if menu_item.stock_quantity > 0 and not menu_item.is_available and menu_item.track_stock:
            menu_item.is_available = True
            messages.info(request, f'{menu_item.name} automatically re-enabled (stock available)')
        
        menu_item.save()
        return redirect('manage_menu', restaurant_id=menu_item.category.restaurant.id)
    
    return redirect('dashboard')

@login_required
def restaurant_orders(request, restaurant_id):
    """View orders for a specific restaurant"""
    if request.user.role != 'restaurant_owner':
        messages.error(request, 'Access denied. Restaurant owners only.')
        return redirect('dashboard')
    
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'restaurant': restaurant,
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'restaurants/restaurant_orders.html', context)

@login_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.user.role != 'restaurant_owner':
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, restaurant__owner=request.user)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {order.get_status_display()}',
                'new_status': order.status,
                'new_status_display': order.get_status_display()
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

from core.email_service import send_order_status_update

# In the update_order_status function, add after status update:
@login_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.user.role != 'restaurant_owner':
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, restaurant__owner=request.user)
        new_status = request.POST.get('status')
        old_status = order.status  # Save old status for email
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Send status update email to customer
            send_order_status_update(order, old_status, new_status)
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {order.get_status_display()}',
                'new_status': order.status,
                'new_status_display': order.get_status_display()
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# ... KEEP YOUR EXISTING VIEWS ...

# ============================================================================
# CATEGORY EDIT/DELETE VIEWS
# ============================================================================

@login_required
def edit_category(request, category_id):
    """Edit category - Owner only"""
    category = get_object_or_404(Category, id=category_id)
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    # Check permission
    if request.user != category.restaurant.owner and not is_admin:
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description', '')
            category.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Category updated successfully'})
            else:
                messages.success(request, 'Category updated successfully')
                return redirect('manage_menu', restaurant_id=category.restaurant.id)
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)})
            else:
                messages.error(request, f'Error updating category: {str(e)}')
                return redirect('manage_menu', restaurant_id=category.restaurant.id)

@login_required
def delete_category(request, category_id):
    """Delete category - Owner only"""
    category = get_object_or_404(Category, id=category_id)
    restaurant_id = category.restaurant.id
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    # Check permission
    if request.user != category.restaurant.owner and not is_admin:
        messages.error(request, 'Permission denied')
        return redirect('manage_menu', restaurant_id=restaurant_id)
    
    if request.method == 'POST':
        try:
            category_name = category.name
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
    
    return redirect('manage_menu', restaurant_id=restaurant_id)

# ============================================================================
# MENU ITEM EDIT/DELETE VIEWS
# ============================================================================

@login_required
def edit_menu_item(request, item_id):
    """Edit menu item - Owner only"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    user = request.user
    is_admin = user.role == 'admin' or user.is_superuser or user.is_staff
    
    # Check permission
    if request.user != menu_item.category.restaurant.owner and not is_admin:
        messages.error(request, 'Permission denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            menu_item.name = request.POST.get('name')
            menu_item.description = request.POST.get('description', '')
            menu_item.price = request.POST.get('price')
            menu_item.preparation_time = request.POST.get('preparation_time')
            
            # Handle stock tracking
            menu_item.track_stock = request.POST.get('track_stock') == 'on'
            if menu_item.track_stock:
                menu_item.stock_quantity = int(request.POST.get('stock_quantity', 0))
                menu_item.low_stock_threshold = int(request.POST.get('low_stock_threshold', 5))
                # Auto-disable if out of stock
                if menu_item.stock_quantity == 0:
                    menu_item.is_available = False
            
            # Handle image upload
            if request.FILES.get('image'):
                menu_item.image = request.FILES.get('image')
            
            menu_item.save()
            
            messages.success(request, 'Menu item updated successfully!')
            return redirect('manage_menu', restaurant_id=menu_item.category.restaurant.id)
                
        except Exception as e:
            messages.error(request, f'Error updating menu item: {str(e)}')
            return redirect('manage_menu', restaurant_id=menu_item.category.restaurant.id)

@login_required
def delete_menu_item(request, item_id):
    """Delete menu item - Owner only"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    restaurant_id = menu_item.category.restaurant.id
    
    # Check permission
    if request.user != menu_item.category.restaurant.owner and request.user.role != 'admin':
        messages.error(request, 'Permission denied')
        return redirect('manage_menu', restaurant_id=restaurant_id)
    
    if request.method == 'POST':
        try:
            item_name = menu_item.name
            menu_item.delete()
            messages.success(request, f'Menu item "{item_name}" deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting menu item: {str(e)}')
    
    return redirect('manage_menu', restaurant_id=restaurant_id)

# ============================================================================
# UPDATE MANAGE_MENU VIEW TO INCLUDE STATS
# ============================================================================

@login_required
def manage_menu(request, restaurant_id):
    """Manage restaurant menu items and categories - Owner only"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check permission
    if request.user != restaurant.owner and request.user.role != 'admin':
        messages.error(request, "You don't have permission to manage this menu.")
        return redirect('dashboard')
    
    # Get menu items and categories for this restaurant
    menu_items = MenuItem.objects.filter(category__restaurant=restaurant)
    categories = Category.objects.filter(restaurant=restaurant)
    
    # Calculate stats
    total_items = menu_items.count()
    available_items = menu_items.filter(is_available=True).count()
    
    # Calculate revenue from completed orders
    completed_orders = Order.objects.filter(
        restaurant=restaurant, 
        status='completed'
    )
    total_revenue = sum(order.total_price for order in completed_orders)
    
    if request.method == 'POST':
        # Handle menu item creation
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


# ==================== STAFF MANAGEMENT ====================

@login_required
def manage_staff(request, slug):
    """View and manage restaurant staff - Owner only"""
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    # Check permission - only owner can manage staff
    if request.user != restaurant.owner:
        messages.error(request, "Only the restaurant owner can manage staff.")
        return redirect('restaurant_dashboard', slug=slug)
    
    staff_members = Staff.objects.filter(restaurant=restaurant).select_related('user')
    pending_invites = StaffInvite.objects.filter(restaurant=restaurant, is_accepted=False)
    
    context = {
        'restaurant': restaurant,
        'staff_members': staff_members,
        'pending_invites': pending_invites,
        'role_choices': Staff.ROLE_CHOICES,
        'role_permissions': Staff.ROLE_PERMISSIONS,
    }
    return render(request, 'restaurants/manage_staff.html', context)


@login_required
def invite_staff(request, slug):
    """Send staff invitation - Owner only"""
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    if request.user != restaurant.owner:
        messages.error(request, "Only the restaurant owner can invite staff.")
        return redirect('restaurant_dashboard', slug=slug)
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role')
        
        if not email or not role:
            messages.error(request, "Email and role are required.")
            return redirect('manage_staff', slug=slug)
        
        # Check if already a staff member
        existing_staff = Staff.objects.filter(
            restaurant=restaurant,
            user__email=email
        ).exists()
        
        if existing_staff:
            messages.error(request, f"{email} is already a staff member.")
            return redirect('manage_staff', slug=slug)
        
        # Check for pending invite
        pending = StaffInvite.objects.filter(
            restaurant=restaurant,
            email=email,
            is_accepted=False
        ).first()
        
        if pending and not pending.is_expired:
            messages.warning(request, f"An invitation is already pending for {email}.")
            return redirect('manage_staff', slug=slug)
        
        # Delete expired invites
        StaffInvite.objects.filter(
            restaurant=restaurant,
            email=email,
            is_accepted=False
        ).delete()
        
        # Create new invite
        invite_code = Staff.generate_invite_code()
        expires_at = timezone.now() + timedelta(days=7)
        
        invite = StaffInvite.objects.create(
            restaurant=restaurant,
            email=email,
            role=role,
            invite_code=invite_code,
            invited_by=request.user,
            expires_at=expires_at
        )
        
        # TODO: Send email notification
        # For now, show the invite link
        invite_url = request.build_absolute_uri(f'/staff/accept-invite/{invite_code}/')
        
        messages.success(
            request, 
            f"Invitation sent to {email}! Share this link: {invite_url}"
        )
        
        return redirect('manage_staff', slug=slug)
    
    return redirect('manage_staff', slug=slug)


@login_required
def update_staff(request, slug, staff_id):
    """Update staff role or status - Owner only"""
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    if request.user != restaurant.owner:
        messages.error(request, "Only the restaurant owner can update staff.")
        return redirect('restaurant_dashboard', slug=slug)
    
    staff = get_object_or_404(Staff, id=staff_id, restaurant=restaurant)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_role':
            new_role = request.POST.get('role')
            if new_role in dict(Staff.ROLE_CHOICES):
                staff.role = new_role
                staff.save()
                messages.success(request, f"Updated {staff.user.get_full_name() or staff.user.username}'s role to {staff.get_role_display()}.")
        
        elif action == 'toggle_active':
            staff.is_active = not staff.is_active
            staff.save()
            status = "activated" if staff.is_active else "deactivated"
            messages.success(request, f"Staff member {status}.")
        
        elif action == 'remove':
            name = staff.user.get_full_name() or staff.user.username
            staff.delete()
            messages.success(request, f"{name} has been removed from staff.")
    
    return redirect('manage_staff', slug=slug)


@login_required
def cancel_invite(request, slug, invite_id):
    """Cancel a pending staff invitation - Owner only"""
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    if request.user != restaurant.owner:
        messages.error(request, "Only the restaurant owner can cancel invitations.")
        return redirect('restaurant_dashboard', slug=slug)
    
    invite = get_object_or_404(StaffInvite, id=invite_id, restaurant=restaurant)
    
    if request.method == 'POST':
        invite.delete()
        messages.success(request, f"Invitation to {invite.email} cancelled.")
    
    return redirect('manage_staff', slug=slug)


def accept_staff_invite(request, invite_code):
    """Accept a staff invitation - Creates staff record"""
    invite = get_object_or_404(StaffInvite, invite_code=invite_code)
    
    if invite.is_accepted:
        messages.error(request, "This invitation has already been used.")
        return redirect('login')
    
    if invite.is_expired:
        messages.error(request, "This invitation has expired. Please request a new one.")
        return redirect('login')
    
    if request.user.is_authenticated:
        # User is logged in - accept invitation
        if request.method == 'POST':
            # Check if already staff at this restaurant
            existing = Staff.objects.filter(user=request.user, restaurant=invite.restaurant).first()
            if existing:
                messages.error(request, f"You're already a staff member at {invite.restaurant.name}.")
                return redirect('staff_dashboard', slug=invite.restaurant.slug)
            
            # Create staff record
            Staff.objects.create(
                user=request.user,
                restaurant=invite.restaurant,
                role=invite.role,
                invite_accepted=True,
                invited_by=invite.invited_by,
                invited_at=invite.invited_at
            )
            
            # Mark invite as accepted
            invite.is_accepted = True
            invite.accepted_at = timezone.now()
            invite.accepted_by = request.user
            invite.save()
            
            messages.success(request, f"Welcome! You're now a {invite.get_role_display()} at {invite.restaurant.name}.")
            return redirect('staff_dashboard', slug=invite.restaurant.slug)
        
        context = {
            'invite': invite,
            'restaurant': invite.restaurant,
        }
        return render(request, 'restaurants/accept_invite.html', context)
    else:
        # Not logged in - redirect to login/register
        request.session['pending_invite_code'] = invite_code
        messages.info(request, "Please login or register to accept this staff invitation.")
        return redirect('login')


@login_required
def staff_dashboard(request, slug):
    """Dashboard for staff members - role-based access"""
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    # Get staff record
    staff = Staff.get_staff_for_user(request.user, restaurant)
    
    # Owner has full access
    is_owner = request.user == restaurant.owner
    
    if not staff and not is_owner:
        messages.error(request, "You don't have staff access to this restaurant.")
        return redirect('home')
    
    # Get orders based on permissions
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')
    
    # Filter orders for kitchen staff (only show preparing orders)
    if staff and staff.role == 'kitchen':
        orders = orders.filter(status__in=['confirmed', 'preparing'])
    
    # Get recent orders
    recent_orders = orders[:20]
    
    # Stats
    today = timezone.now().date()
    today_orders = orders.filter(created_at__date=today)
    
    context = {
        'restaurant': restaurant,
        'staff': staff,
        'is_owner': is_owner,
        'orders': recent_orders,
        'today_orders_count': today_orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'preparing_orders': orders.filter(status='preparing').count(),
        'ready_orders': orders.filter(status='ready').count(),
        'permissions': staff.permissions if staff else Staff.ROLE_PERMISSIONS['manager'],  # Owner gets manager perms
    }
    return render(request, 'restaurants/staff_dashboard.html', context)


@login_required  
def staff_update_order(request, slug, order_id):
    """Staff action to update order status"""
    restaurant = get_object_or_404(Restaurant, slug=slug)
    order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    
    # Check staff permission
    staff = Staff.get_staff_for_user(request.user, restaurant)
    is_owner = request.user == restaurant.owner
    
    if not staff and not is_owner:
        messages.error(request, "You don't have permission.")
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Kitchen staff can only: confirmed -> preparing -> ready
        if staff and staff.role == 'kitchen':
            allowed_transitions = {
                'confirmed': 'preparing',
                'preparing': 'ready'
            }
            if action == 'next_status' and order.status in allowed_transitions:
                order.status = allowed_transitions[order.status]
                order.save()
                messages.success(request, f"Order #{order.id} is now {order.get_status_display()}.")
            else:
                messages.error(request, "You don't have permission for this action.")
        
        # Waiter can: ready -> completed + confirm payment
        elif staff and staff.role == 'waiter':
            if action == 'mark_delivered' and order.status == 'ready':
                order.status = 'completed'
                order.save()
                messages.success(request, f"Order #{order.id} marked as delivered.")
            elif action == 'confirm_cash' and order.payment_method == 'cash':
                order.payment_status = 'confirmed'
                # Also update order status if appropriate
                if order.status in ['pending', 'awaiting_confirmation', 'confirmed']:
                    order.status = 'completed'
                order.save()
                messages.success(request, f"Cash payment confirmed for Order #{order.id}.")
            else:
                messages.error(request, "You don't have permission for this action.")
        
        # Cashier can: confirm payments
        elif staff and staff.role == 'cashier':
            if action in ['confirm_cash', 'confirm_payment']:
                order.payment_status = 'confirmed'
                # Also update order status if appropriate
                if order.status in ['pending', 'awaiting_confirmation', 'confirmed']:
                    order.status = 'completed'
                order.save()
                messages.success(request, f"Payment confirmed for Order #{order.id}.")
            else:
                messages.error(request, "You don't have permission for this action.")
        
        # Manager and Owner can do everything
        elif staff and staff.role == 'manager' or is_owner:
            if action == 'update_status':
                new_status = request.POST.get('status')
                if new_status:
                    order.status = new_status
                    order.save()
                    messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
            elif action in ['confirm_cash', 'confirm_payment']:
                order.payment_status = 'confirmed'
                # Also update order status if appropriate
                if order.status in ['pending', 'awaiting_confirmation', 'confirmed']:
                    order.status = 'completed'
                order.save()
                messages.success(request, f"Payment confirmed for Order #{order.id}.")
    
    return redirect('staff_dashboard', slug=slug)

from django.views.decorators.http import require_POST

@require_POST
@login_required
def bulk_update_order_status(request, restaurant_id):
    """Bulk update status for selected orders"""
    if request.user.role != 'restaurant_owner':
        messages.error(request, 'Access denied. Restaurant owners only.')
        return redirect('restaurant_orders', restaurant_id=restaurant_id)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    order_ids = request.POST.getlist('order_ids')
    new_status = request.POST.get('status')

    if not order_ids or not new_status:
        messages.error(request, 'Please select orders and a status to apply.')
        return redirect('restaurant_orders', restaurant_id=restaurant_id)

    valid_statuses = dict(Order.STATUS_CHOICES)
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status selected.')
        return redirect('restaurant_orders', restaurant_id=restaurant_id)

    updated_count = 0
    for order in Order.objects.filter(id__in=order_ids, restaurant=restaurant):
        if order.status != new_status:
            order.status = new_status
            order.save()
            updated_count += 1
    messages.success(request, f"Updated {updated_count} order(s) to '{valid_statuses[new_status]}'.")
    return redirect('restaurant_orders', restaurant_id=restaurant_id)