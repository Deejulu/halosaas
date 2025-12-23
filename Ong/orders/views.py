from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Order, OrderItem
from restaurants.models import Restaurant, MenuItem
from .cart import Cart
from django.http import JsonResponse
from django.urls import reverse

@login_required
def create_order(request, restaurant_slug):
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    categories = restaurant.category_set.prefetch_related('menuitem_set').all()
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
    }
    return render(request, 'orders/create_order.html', context)

@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
        cart = Cart(request)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            special_requests = request.POST.get('special_requests', '')
            
            cart.add(menu_item, quantity, special_requests)
            # Debug logging of session cart state after add
            import logging
            logger = logging.getLogger(__name__)
            try:
                logger.debug('Session cart after add: %s', request.session.get('cart'))
                logger.debug('Current cart restaurant: %s', request.session.get('current_cart_restaurant'))
            except Exception:
                logger.exception('Failed to log session cart')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'cart_total_items': cart.get_total_items(),
                    'message': f'{menu_item.name} added to cart!'
                })
            else:
                messages.success(request, f'{menu_item.name} added to cart!')
                return redirect('restaurant_detail', slug=menu_item.category.restaurant.slug)
                
        except ValueError as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            else:
                messages.error(request, str(e))
                return redirect('restaurant_detail', slug=menu_item.category.restaurant.slug)
    
    return redirect('home')

@login_required
def view_cart(request):
    cart = Cart(request)
    cart_items = list(cart)
    total_price = cart.get_total_price()
    # Debug logging to inspect why cart might be empty
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.debug('Viewing cart - session cart: %s', request.session.get('cart'))
        logger.debug('Viewing cart - current_cart_restaurant: %s', request.session.get('current_cart_restaurant'))
        logger.debug('Cart items computed: %s', cart_items)
    except Exception:
        logger.exception('Failed to log cart view state')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart': cart
    }
    return render(request, 'orders/cart.html', context)


@login_required
def switch_cart_restaurant(request, restaurant_id):
    """Set the active cart restaurant (from session subcarts) and redirect to cart view."""
    # store as string for consistency with session keys
    request.session['current_cart_restaurant'] = str(restaurant_id)
    request.session.modified = True
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        cart = Cart(request)
        
        quantity = int(request.POST.get('quantity', 1))
        special_requests = request.POST.get('special_requests', '')
        
        print(f"DEBUG: Updating item {item_id} to quantity {quantity}")
        print(f"DEBUG: Cart before: {cart.cart}")
        
        cart.update(menu_item, quantity, special_requests)
        
        print(f"DEBUG: Cart after: {cart.cart}")
        
        messages.success(request, f'Cart updated! {menu_item.name} x {quantity}')
        return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        cart = Cart(request)
        cart.remove(menu_item)
        
        messages.success(request, 'Item removed from cart!')
        return redirect('view_cart')

@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart.clear()
        messages.success(request, 'Cart cleared!')
        return redirect('view_cart')

@login_required
def checkout(request):
    cart = Cart(request)
    
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('view_cart')
    
    cart_items = list(cart)
    total_price = cart.get_total_price()
    restaurant_id = cart.get_restaurant_id()
    
    if restaurant_id:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    else:
        messages.error(request, 'No restaurant selected!')
        return redirect('view_cart')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'restaurant': restaurant,
        'cart': cart
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def process_checkout(request):
    """Process checkout based on selected payment method"""
    if request.method != 'POST':
        return redirect('checkout')
    
    cart = Cart(request)
    
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('view_cart')
    
    cart_items = list(cart)
    total_price = cart.get_total_price()
    restaurant_id = cart.get_restaurant_id()
    
    if not restaurant_id:
        messages.error(request, 'No restaurant selected!')
        return redirect('view_cart')
    
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    payment_method = request.POST.get('payment_method', 'cash')
    
    # Validate cart items are still available
    for item in cart_items:
        menu_item = get_object_or_404(MenuItem, id=item['menu_item_id'])
        if not menu_item.is_available:
            messages.error(request, f"{menu_item.name} is no longer available. Please update your cart.")
            return redirect('view_cart')
    
    try:
        # Determine initial status based on payment method
        if payment_method == 'cash':
            order_status = 'confirmed'
            payment_status = 'pending'  # Will be confirmed on delivery
        elif payment_method == 'paystack':
            # Redirect to Paystack flow
            return redirect('payments:initiate_payment')
        elif payment_method in ['bank_transfer', 'mobile_money']:
            order_status = 'awaiting_confirmation'
            payment_status = 'awaiting_confirmation'
        elif payment_method == 'pos':
            order_status = 'confirmed'
            payment_status = 'pending'  # Will be confirmed at pickup
        else:
            order_status = 'pending'
            payment_status = 'pending'
        
        # Create order
        order = Order.objects.create(
            customer=request.user,
            restaurant=restaurant,
            total_price=total_price,
            customer_name=request.user.get_full_name() or request.user.username,
            customer_phone=request.user.phone_number or '',
            customer_email=request.user.email,
            payment_method=payment_method,
            payment_status=payment_status,
            status=order_status,
        )
        
        # Handle payment proof upload (for bank transfer / mobile money)
        if request.FILES.get('payment_proof'):
            order.payment_proof = request.FILES['payment_proof']
            order.save()
        
        # Create order items
        for item in cart_items:
            menu_item = get_object_or_404(MenuItem, id=item['menu_item_id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item['quantity'],
                price=item['price'],
                special_requests=item['special_requests']
            )
        
        # Clear cart
        cart.clear()
        
        # Send notifications
        try:
            from core.email_service import send_order_confirmation, send_order_notification_to_restaurant
            send_order_confirmation(order)
            send_order_notification_to_restaurant(order)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        # Redirect based on payment method
        if payment_method == 'cash':
            messages.success(request, 'Order placed successfully! Pay cash on delivery.')
        elif payment_method in ['bank_transfer', 'mobile_money']:
            messages.success(request, 'Order placed! We\'re awaiting your payment confirmation.')
        elif payment_method == 'pos':
            messages.success(request, 'Order placed successfully! Pay at pickup with POS.')
        else:
            messages.success(request, 'Order placed successfully!')
        
        return redirect('order_detail', order_id=order.id)
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('checkout')


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user has permission to view this order
    if request.user.role == 'customer' and order.customer != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('order_history')
    elif request.user.role == 'restaurant_owner' and order.restaurant.owner != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('order_history')
    
    order_items = order.orderitem_set.all()
    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_history(request):
    # Optional filter: ?restaurant=<slug> to show orders for a specific restaurant
    restaurant_slug = request.GET.get('restaurant')
    restaurant = None
    if restaurant_slug:
        try:
            restaurant = Restaurant.objects.get(slug=restaurant_slug)
        except Restaurant.DoesNotExist:
            restaurant = None

    # Build base queryset depending on role
    if request.user.role == 'customer':
        orders = Order.objects.filter(customer=request.user)
        if restaurant:
            orders = orders.filter(restaurant=restaurant)
    elif request.user.role == 'restaurant_owner':
        orders = Order.objects.filter(restaurant__owner=request.user)
        if restaurant:
            # only allow owner to filter by their own restaurant
            if restaurant.owner == request.user:
                orders = orders.filter(restaurant=restaurant)
            else:
                orders = Order.objects.none()
    else:
        orders = Order.objects.all()
        if restaurant:
            orders = orders.filter(restaurant=restaurant)

    orders = orders.order_by('-created_at')

    # Force evaluation to avoid stale cache
    orders = list(orders)

    context = {
        'orders': orders,
        'filter_restaurant': restaurant,
    }
    return render(request, 'orders/order_history.html', context)


@login_required
def ajax_restaurant_orders(request, restaurant_slug):
    """Return paginated JSON of the requesting customer's orders for a given restaurant."""
    if not request.user.is_authenticated or request.user.role != 'customer':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    per = 5
    offset = (page - 1) * per

    qs = Order.objects.filter(customer=request.user, restaurant=restaurant).order_by('-created_at')
    total = qs.count()
    orders = qs[offset:offset+per]

    data = []
    for o in orders:
        data.append({
            'id': o.id,
            'status': o.get_status_display(),
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
            'total_price': str(o.total_price),
            'detail_url': reverse('order_detail', args=[o.id])
        })

    return JsonResponse({'orders': data, 'total': total, 'page': page, 'per': per})


@login_required
def confirm_payment(request, order_id):
    """Restaurant owner confirms payment received"""
    if request.method != 'POST':
        return redirect('order_detail', order_id=order_id)
    
    order = get_object_or_404(Order, id=order_id)
    
    # Only restaurant owner can confirm payment
    if request.user.role != 'restaurant_owner' or order.restaurant.owner != request.user:
        messages.error(request, 'You do not have permission to confirm this payment.')
        return redirect('order_detail', order_id=order_id)
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Confirming payment for order {order.id} (current status: {order.status}, payment_status: {order.payment_status})")
    # Update payment status
    order.payment_status = 'confirmed'
    # If order was pending or awaiting confirmation, now mark as completed
    if order.status in ['pending', 'awaiting_confirmation', 'confirmed']:
        logger.info(f"Order {order.id} status changing from {order.status} to completed")
        order.status = 'completed'
    order.save()
    logger.info(f"Order {order.id} after save: status={order.status}, payment_status={order.payment_status}")
    
    # Send notification to customer
    try:
        from core.email_service import send_payment_confirmation_to_customer
        send_payment_confirmation_to_customer(order)
    except Exception as e:
        print(f"Email sending failed: {e}")
    
    messages.success(request, 'Payment confirmed successfully!')
    return redirect('order_detail', order_id=order_id)


@login_required
def reject_payment(request, order_id):
    """Restaurant owner rejects payment (not received)"""
    if request.method != 'POST':
        return redirect('order_detail', order_id=order_id)
    
    order = get_object_or_404(Order, id=order_id)
    
    # Only restaurant owner can reject payment
    if request.user.role != 'restaurant_owner' or order.restaurant.owner != request.user:
        messages.error(request, 'You do not have permission to reject this payment.')
        return redirect('order_detail', order_id=order_id)
    
    # Update payment status
    order.payment_status = 'failed'
    order.status = 'cancelled'
    order.save()
    
    # Send notification to customer
    try:
        from core.email_service import send_payment_rejected_notification
        send_payment_rejected_notification(order)
    except Exception as e:
        print(f"Email sending failed: {e}")
    
    messages.warning(request, 'Payment marked as not received. Order cancelled.')
    return redirect('order_detail', order_id=order_id)


@login_required
def update_order_status(request, order_id):
    """Restaurant owner updates order status"""
    order = get_object_or_404(Order, id=order_id)
    
    # Only restaurant owner can update status
    if request.user.role != 'restaurant_owner' or order.restaurant.owner != request.user:
        messages.error(request, 'You do not have permission to update this order.')
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['pending', 'awaiting_confirmation', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status.')
        
        return redirect('order_detail', order_id=order_id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/update_status.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel an order - for customers (pending/cash orders) and restaurant owners"""
    if request.method != 'POST':
        return redirect('order_detail', order_id=order_id)
    
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    is_customer = request.user.role == 'customer' and order.customer == request.user
    is_owner = request.user.role == 'restaurant_owner' and order.restaurant.owner == request.user
    is_admin = request.user.is_superuser
    
    if not (is_customer or is_owner or is_admin):
        messages.error(request, 'You do not have permission to cancel this order.')
        return redirect('order_detail', order_id=order_id)
    
    # Customers can only cancel pending orders or orders with cash payment that aren't completed
    if is_customer:
        cancellable_statuses = ['pending', 'confirmed', 'awaiting_confirmation']
        if order.status not in cancellable_statuses:
            messages.error(request, 'This order cannot be cancelled at this stage.')
            return redirect('order_detail', order_id=order_id)
        
        # Don't allow cancellation if already preparing or beyond
        if order.status in ['preparing', 'ready', 'completed']:
            messages.error(request, 'Order is already being prepared and cannot be cancelled.')
            return redirect('order_detail', order_id=order_id)
    
    # Cancel the order
    order.status = 'cancelled'
    order.save()
    
    # Send notification
    try:
        from core.email_service import send_order_cancelled_notification
        send_order_cancelled_notification(order, cancelled_by=request.user)
    except Exception as e:
        print(f"Email sending failed: {e}")
    
    messages.success(request, 'Order has been cancelled.')
    return redirect('order_detail', order_id=order_id)