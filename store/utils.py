from .models import Order, Product

def get_cart_data(request):
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(customer=request.user.customer, complete=False)
            return {
                'cart_items_count': order.get_cart_items,
                'cart_items': [],
            }
        except Exception:
            return {
                'cart_items_count': 0,
                'cart_items': [],
            }

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

def get_cart_items_and_total(request):
    cart_items = []
    cart_total = 0

    if request.user.is_authenticated:
        try:
            order = Order.objects.get(customer=request.user.customer, complete=False)
        except Exception:
            order = None

        if order:
            for item in order.orderitem_set.all():
                total_price = float(item.get_total_price)
                cart_items.append({
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'image_url': item.product.imageURL,
                    'price': float(item.product.price),
                    'quantity': item.quantity,
                    'total_price': total_price
                })
                cart_total += total_price
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total_price = float(product.price) * quantity
                cart_items.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'image_url': product.imageURL,
                    'price': float(product.price),
                    'quantity': quantity,
                    'total_price': total_price
                })
                cart_total += total_price
            except Product.DoesNotExist:
                continue

    return cart_items, cart_total
