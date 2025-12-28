from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Order

@login_required
def delete_order(request, order_id):
    """Allow customers to delete their own canceled orders."""
    order = get_object_or_404(Order, id=order_id)
    if request.user.role != 'customer' or order.customer != request.user:
        messages.error(request, 'You do not have permission to delete this order.')
        return redirect('order_history')
    if order.status != 'cancelled':
        messages.error(request, 'Only canceled orders can be deleted.')
        return redirect('order_history')
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Canceled order deleted successfully.')
        return redirect('order_history')
    messages.error(request, 'Invalid request.')
    return redirect('order_history')
