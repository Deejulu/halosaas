from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import hmac
import hashlib

from .models import Payment
from orders.models import Order, OrderItem
from restaurants.models import MenuItem, Restaurant
from orders.cart import Cart
from .services import PaystackService, generate_payment_reference
from core.email_service import send_order_confirmation, send_order_notification_to_restaurant, send_payment_confirmation
from django.http import JsonResponse
from django.urls import reverse

@login_required
def initiate_payment(request):
    """Initiate payment process - create order and redirect to Paystack"""
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
    
    # Get restaurant
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Validate cart items are still available
    for item in cart_items:
        menu_item = get_object_or_404(MenuItem, id=item['menu_item_id'])
        if not menu_item.is_available:
            messages.error(request, f"{menu_item.name} is no longer available. Please update your cart.")
            return redirect('view_cart')
    
    try:
        # Create order first
        order = Order.objects.create(
            customer=request.user,
            restaurant=restaurant,
            total_price=total_price,
            customer_name=request.user.get_full_name() or request.user.username,
            customer_phone=request.user.phone_number or '',
            customer_email=request.user.email or f"{request.user.username}@example.com"
        )
        
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
        
        # Create payment record
        payment_reference = generate_payment_reference()
        payment = Payment.objects.create(
            order=order,
            amount=total_price,
            reference=payment_reference,
            customer_email=request.user.email or f"{request.user.username}@example.com",
            customer_name=request.user.get_full_name() or request.user.username
        )
        
        # Initialize Paystack payment
        paystack_service = PaystackService()
        callback_url = request.build_absolute_uri(reverse('payments:payment_verification', args=[payment_reference]))
        
        # Ensure we have an email for Paystack
        customer_email = request.user.email
        if not customer_email:
            customer_email = f"{request.user.username}@example.com"  # Fallback for test users
        
        response = paystack_service.initialize_transaction(
            email=customer_email,
            amount=total_price,
            reference=payment_reference,
            callback_url=callback_url
        )
        
        if response.get('status'):
            payment_url = response['data']['authorization_url']
            return redirect(payment_url)
        else:
            # Payment initialization failed - show more details
            error_msg = response.get('message', 'Unknown error')
            print(f"Paystack Error: {response}")  # Debug log
            
            # Check for common errors
            if '1010' in error_msg or '403' in error_msg:
                messages.error(request, 'Online payment is temporarily unavailable. Please try Cash on Delivery or POS payment.')
            else:
                messages.error(request, f'Payment initialization failed: {error_msg}')
            
            # Delete the created order since payment failed
            order.delete()
            return redirect('checkout')
            
    except Exception as e:
        print(f"Payment Exception: {str(e)}")  # Debug log
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('checkout')

@login_required
def payment_verification(request, reference):
    """Verify Paystack payment and update order status"""
    payment = get_object_or_404(Payment, reference=reference)
    paystack_service = PaystackService()
    
    verification = paystack_service.verify_transaction(reference)
    
    if verification.get('status') and verification['data']['status'] == 'success':
        # Payment successful
        payment.status = 'success'
        payment.paystack_reference = verification['data']['reference']
        payment.gateway_response = json.dumps(verification['data'])
        payment.save()
        
        # Update order status
        payment.order.status = 'confirmed'
        payment.order.save()
        
        # Clear cart
        cart = Cart(request)
        cart.clear()
        
        # Send email notifications
        try:
            send_order_confirmation(payment.order)
            send_order_notification_to_restaurant(payment.order)
            send_payment_confirmation(payment)
        except Exception as e:
            # Log email error but don't break the flow
            print(f"Email sending failed: {e}")
        
        messages.success(request, 'Payment successful! Your order has been confirmed.')
        return redirect('payments:payment_success', reference=reference)
    else:
        # Payment failed
        payment.status = 'failed'
        payment.gateway_response = json.dumps(verification)
        payment.save()
        
        # Update order status to reflect payment failure
        payment.order.status = 'cancelled'
        payment.order.save()
        
        messages.error(request, 'Payment failed. Please try again.')
        return redirect('payments:payment_failed', reference=reference)

@login_required
def payment_success(request, reference):
    """Display payment success page"""
    payment = get_object_or_404(Payment, reference=reference)
    
    # Verify user has permission to view this payment
    if payment.order.customer != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this payment.')
        return redirect('dashboard')
    
    context = {
        'payment': payment,
        'order': payment.order,
        'order_items': payment.order.orderitem_set.all()
    }
    return render(request, 'payments/success.html', context)

@login_required
def payment_failed(request, reference):
    """Display payment failure page"""
    payment = get_object_or_404(Payment, reference=reference)
    
    # Verify user has permission to view this payment
    if payment.order.customer != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this payment.')
        return redirect('dashboard')
    
    context = {
        'payment': payment
    }
    return render(request, 'payments/failed.html', context)

@login_required
def payment_history(request):
    """Display user's payment history"""
    # Optional filter param: ?restaurant=<slug>
    restaurant_slug = request.GET.get('restaurant')
    restaurant = None
    if restaurant_slug:
        try:
            restaurant = Restaurant.objects.get(slug=restaurant_slug)
        except Restaurant.DoesNotExist:
            restaurant = None

    if request.user.role == 'customer':
        payments = Payment.objects.filter(order__customer=request.user)
        if restaurant:
            payments = payments.filter(order__restaurant=restaurant)
    elif request.user.role == 'restaurant_owner':
        payments = Payment.objects.filter(order__restaurant__owner=request.user)
        if restaurant:
            if restaurant.owner == request.user:
                payments = payments.filter(order__restaurant=restaurant)
            else:
                payments = Payment.objects.none()
    else:
        payments = Payment.objects.all()
        if restaurant:
            payments = payments.filter(order__restaurant=restaurant)

    payments = payments.order_by('-created_at')

    context = {
        'payments': payments,
        'filter_restaurant': restaurant,
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def ajax_restaurant_payments(request, restaurant_slug):
    """Return paginated JSON of the requesting customer's payments for a given restaurant."""
    if not request.user.is_authenticated or request.user.role != 'customer':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    per = 5
    offset = (page - 1) * per

    qs = Payment.objects.filter(order__customer=request.user, order__restaurant=restaurant).order_by('-created_at')
    total = qs.count()
    payments = qs[offset:offset+per]

    data = []
    for p in payments:
        data.append({
            'reference': p.reference,
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
            'amount': str(p.amount),
            'detail_url': reverse('payments:payment_detail', args=[p.reference])
        })

    return JsonResponse({'payments': data, 'total': total, 'page': page, 'per': per})

@login_required
def payment_detail(request, reference):
    """Display payment details"""
    payment = get_object_or_404(Payment, reference=reference)
    
    # Verify user has permission to view this payment
    if (payment.order.customer != request.user and 
        payment.order.restaurant.owner != request.user and 
        not request.user.is_staff):
        messages.error(request, 'You do not have permission to view this payment.')
        return redirect('dashboard')
    
    context = {
        'payment': payment,
        'order': payment.order,
        'order_items': payment.order.orderitem_set.all()
    }
    return render(request, 'payments/payment_detail.html', context)

# Webhook for Paystack (for production)
@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook for payment verification"""
    if request.method == 'POST':
        try:
            # Verify signature using PAYSTACK_WEBHOOK_SECRET
            signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
            secret = getattr(settings, 'PAYSTACK_WEBHOOK_SECRET', '')

            # If webhook secret is configured, verify the signature
            if secret:
                computed = hmac.new(secret.encode('utf-8'), request.body or b'', hashlib.sha512).hexdigest()
                if not hmac.compare_digest(computed, signature):
                    return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)

            payload = json.loads(request.body)

            # Handle Paystack "charge.success" events
            if payload.get('event') == 'charge.success':
                reference = payload['data']['reference']
                
                # Update payment status
                payment = get_object_or_404(Payment, reference=reference)
                payment.status = 'success'
                payment.paystack_reference = payload['data']['id']
                payment.gateway_response = json.dumps(payload['data'])
                payment.save()
                
                # Update order status
                payment.order.status = 'confirmed'
                payment.order.save()
                
                # Send email notifications
                try:
                    send_order_confirmation(payment.order)
                    send_order_notification_to_restaurant(payment.order)
                    send_payment_confirmation(payment)
                except Exception as e:
                    print(f"Email sending failed in webhook: {e}")
            
            return JsonResponse({'status': 'success'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def retry_payment(request, reference):
    """Retry a failed payment"""
    payment = get_object_or_404(Payment, reference=reference, status='failed')
    
    # Verify user has permission to retry this payment
    if payment.order.customer != request.user:
        messages.error(request, 'You do not have permission to retry this payment.')
        return redirect('dashboard')
    
    # Re-initialize payment with Paystack
    paystack_service = PaystackService()
    callback_url = request.build_absolute_uri(f'/payment/verify/{reference}/')
    
    response = paystack_service.initialize_transaction(
        email=payment.customer_email,
        amount=payment.amount,
        reference=reference,
        callback_url=callback_url
    )
    
    if response.get('status'):
        payment_url = response['data']['authorization_url']
        return redirect(payment_url)
    else:
        messages.error(request, 'Failed to initialize payment. Please try again.')
        return redirect('payment_detail', reference=reference)