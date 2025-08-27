from .utils import get_cart_data  

def cart_item_count(request):
    data = get_cart_data(request)
    return {
        'cart_items_count': data['cart_items_count']
    }