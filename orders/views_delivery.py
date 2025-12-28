from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order

@login_required
def choose_delivery_method(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.delivery_method:
        return redirect('order_detail', order_id=order.id)
    if request.method == 'POST':
        method = request.POST.get('delivery_method')
        if method == 'pickup':
            order.delivery_method = 'pickup'
            order.save()
            messages.success(request, 'You selected Pick Up. Please come to the restaurant to collect your order.')
            return redirect('order_detail', order_id=order.id)
        elif method == 'delivery':
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            whatsapp = request.POST.get('whatsapp')
            if not (name and phone and email and whatsapp):
                messages.error(request, 'All delivery info fields are required.')
            else:
                order.delivery_method = 'delivery'
                order.delivery_info = {
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'whatsapp': whatsapp
                }
                order.save()
                messages.success(request, 'Delivery details submitted! We will contact you about your dispatch.')
                return redirect('order_detail', order_id=order.id)
    return render(request, 'orders/choose_delivery_method.html', {'order': order})
