from .models import Product

def get_cart_data(request):
    cart = request.session.get('cart', {})

    cart_items_count = 0
    for item in cart.values():
        if isinstance(item, dict):
            cart_items_count += item.get('quantity', 0)
        else:
            cart_items_count += item  # assume it's an int

    return {
        'cart_items_count': cart_items_count,
        'cart_items': cart,
    }