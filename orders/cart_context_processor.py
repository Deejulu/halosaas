def cart_context(request):
    cart = request.session.get('cart', {})
    total_items = 0
    for subcart in cart.values():
        if isinstance(subcart, dict):
            total_items += sum(item.get('quantity', 0) for item in subcart.values())
    return {
        'cart_total_items': total_items,
        'session_cart': cart,
        'current_cart_restaurant': request.session.get('current_cart_restaurant')
    }
