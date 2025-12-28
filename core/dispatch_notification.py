from .email_service import send_email

def send_dispatch_notification(order):
    if not order.delivery_method == 'delivery' or not order.delivery_info:
        return False
    subject = f"Your Order #{order.id} is Out for Delivery"
    context = {
        'order': order,
        'delivery_info': order.delivery_info,
        'restaurant': order.restaurant,
        'customer': order.customer,
    }
    return send_email(
        subject=subject,
        to_email=order.delivery_info.get('email', order.customer_email),
        template_name='dispatch_notification.html',
        context=context
    )
