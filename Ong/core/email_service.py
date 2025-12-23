from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_email(subject, to_email, template_name, context):
    """
    Send HTML email with fallback to text
    """
    try:
        # Render HTML content
        html_content = render_to_string(f'emails/{template_name}', context)
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_order_confirmation(order):
    """Send order confirmation to customer"""
    subject = f"Order Confirmation - #{order.id}"
    context = {
        'order': order,
        'customer': order.customer,
        'restaurant': order.restaurant,
        'order_items': order.orderitem_set.all(),
    }
    
    return send_email(
        subject=subject,
        to_email=order.customer_email,
        template_name='order_confirmation.html',
        context=context
    )

def send_order_notification_to_restaurant(order):
    """Send new order notification to restaurant owner"""
    subject = f"New Order Received - #{order.id}"
    context = {
        'order': order,
        'restaurant': order.restaurant,
        'order_items': order.orderitem_set.all(),
    }
    
    return send_email(
        subject=subject,
        to_email=order.restaurant.email,
        template_name='new_order_notification.html',
        context=context
    )

def send_payment_confirmation(payment):
    """Send payment confirmation to customer"""
    subject = f"Payment Confirmed - Order #{payment.order.id}"
    context = {
        'payment': payment,
        'order': payment.order,
        'customer': payment.order.customer,
    }
    
    return send_email(
        subject=subject,
        to_email=payment.customer_email,
        template_name='payment_confirmation.html',
        context=context
    )

def send_payment_confirmation_to_customer(order):
    """Send payment confirmation when restaurant owner confirms payment"""
    subject = f"Payment Confirmed - Order #{order.id}"
    context = {
        'order': order,
        'customer': order.customer,
        'restaurant': order.restaurant,
        'payment_method': order.get_payment_method_display(),
    }
    
    return send_email(
        subject=subject,
        to_email=order.customer_email,
        template_name='payment_confirmed_notification.html',
        context=context
    )

def send_payment_rejected_notification(order):
    """Send notification when payment is marked as not received"""
    subject = f"Payment Issue - Order #{order.id}"
    context = {
        'order': order,
        'customer': order.customer,
        'restaurant': order.restaurant,
        'payment_method': order.get_payment_method_display(),
    }
    
    return send_email(
        subject=subject,
        to_email=order.customer_email,
        template_name='payment_rejected_notification.html',
        context=context
    )

def send_order_status_update(order, old_status, new_status):
    """Send order status update to customer"""
    subject = f"Order Update - #{order.id}"
    context = {
        'order': order,
        'customer': order.customer,
        'restaurant': order.restaurant,
        'old_status': old_status,
        'new_status': new_status,
    }
    
    return send_email(
        subject=subject,
        to_email=order.customer_email,
        template_name='order_status_update.html',
        context=context
    )