from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from .models import Customer, Product, Order, OrderItem, ShippingAddress, Category
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import  User
from django.contrib.auth import authenticate, login, logout
from .forms import UserUpdateForm,ProfileUpdateForm
from .utils import get_cart_data, get_cart_items_and_total
import json


# Create your views here.
def index(request):
    products = Product.objects.all().order_by('-id')[:8]  # Show latest 8 products for a balanced grid
    context = {
        'products': products,
    }
    return render(request, "store/index.html", context)

def store(request):
    data = get_cart_data(request)
    cart_items = data['cart_items']

    category_slug = request.GET.get('category')
    categories = Category.objects.all()

    product_list = Product.objects.all().order_by('-id')
    if category_slug:
        product_list = product_list.filter(category__slug=category_slug)

    paginator = Paginator(product_list, 12)  # Increased count for better store experience
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)       
    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'cart_items': cart_items,
        'categories': categories,
        'current_category': category_slug,
    }
    return render(request, 'store/store.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Message from {name} ({email}):\n\n{message}"

        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL], # Send to admin/support
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
        
        return redirect('contact')

    return render(request, 'store/contact.html')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Total completed orders
    total_orders = Order.objects.filter(
        customer=request.user.customer, complete=True
    ).count()

    # Pending orders (only if they have items)
    pending_orders = (
        Order.objects.filter(customer=request.user.customer, complete=False)
        .filter(orderitem__isnull=False)   #  exclude empty carts
        .distinct()
        .count()
    )

    # Last login
    last_login = request.user.last_login

    # Recent orders (latest 5, excluding empty carts)
    order_history = (
        Order.objects.filter(customer=request.user.customer)
        .filter(orderitem__isnull=False)   # exclude empty carts
        .order_by("-date_ordered")[:5]
    )

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "last_login": last_login,
        "order_history": order_history,
    }

    return render(request, 'store/profile.html', context)


# Helper to get or create cart for logged-in user 


# Helper to get session cart for guests 
def get_session_cart(request):
    return request.session.get('cart', {})

# Helper to save session cart back
def save_session_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def get_user_order(request):
    """
    Get or create the current (uncompleted) order for a logged-in user.
    """
    order, created = Order.objects.get_or_create(
        customer=request.user.customer,
        complete=False
    )
    return order

def cart(request):
    """
    Cart page (HTML) and AJAX updater (JSON)
    """
    cart_items, cart_total = get_cart_items_and_total(request)

    # AJAX? -> return JSON (used to update the cart screen without reload)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_items': cart_items,
            'cart_total': float(cart_total)
        })
    
    # Regular request -> render HTML
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        order_total = sum([item.get_total_price for item in items])
    else:
        cart = get_session_cart(request)
        items = []
        order_total = 0
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': subtotal
                })
                order_total += subtotal
            except Product.DoesNotExist:
                continue

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        payment_method = request.POST.get('payment_method')

        if request.user.is_authenticated:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode
            )
            # Decrement stock
            for item in items:
                item.product.stock_count -= item.quantity
                item.product.save()

            order.complete = True
            order.save()
            return redirect('order_complete')
        else:
            # GUEST CHECKOUT: Create records in database
            name = request.POST.get('name')
            email = request.POST.get('email')

            # 1. Get or Create Guest Customer (linked by email)
            existing_customer = Customer.objects.filter(email__iexact=email).order_by('id').first()
            if existing_customer:
                guest_customer = existing_customer
            else:
                guest_customer = Customer.objects.create(
                    email=email,
                    name=name
                )

            # 2. Create the Order
            guest_order = Order.objects.create(
                customer=guest_customer,
                complete=True,
                transaction_id=f"GUEST-{json.dumps(request.session.get('cart', {})).__hash__()}" # Basic unique hash for now
            )

            # 3. Create Shipping Address
            ShippingAddress.objects.create(
                customer=guest_customer,
                order=guest_order,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode
            )

            # 4. Create Order Items and Decrement Stock
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        product=product,
                        order=guest_order,
                        quantity=quantity
                    )
                    product.stock_count -= quantity
                    product.save()
                except Product.DoesNotExist:
                    continue

            # 5. Clear session cart
            request.session['cart'] = {}
            request.session['last_guest_order_id'] = guest_order.id
            request.session.modified = True
            
            return redirect('guest_order_summary') 

    context = {
        'items': items,
        'order_total': order_total
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_complete(request):
    return render(request, 'store/order_complete.html')

def guest_order_summary(request):
    order_id = request.session.get('last_guest_order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            shipping_info = ShippingAddress.objects.filter(order=order).first()
            items = order.orderitem_set.all()
            total = order.get_cart_total
        except Order.DoesNotExist:
            return redirect('store')
    else:
        return redirect('store')

    context = {
        'shipping': shipping_info,
        'items': items,
        'total': total,
        'order_id': order_id
    }

    return render(request, 'store/guest_order_summary.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)

    context = {
        "order": order,
        "items": order.orderitem_set.all(),
    }
    return render(request, "store/order_detail.html", context)

def add_to_cart(request):
    """
    Ajax endpoint for adding items to cart for LOGGED-IN users.
    """
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = Product.objects.get(id=product_id)

        # Get or create active order for user
        order, created = Order.objects.get_or_create(
            customer=request.user.customer,
            complete=False
        )

        # Get or create the order item
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product
        )

        if product.stock_count > order_item.quantity:
            order_item.quantity += 1
            order_item.save()
            cart_count = sum([item.quantity for item in order.orderitem_set.all()])
            return JsonResponse({'cart_count': cart_count})
        else:
            return JsonResponse({'error': 'Not enough stock available'}, status=400)

    return JsonResponse({'error': 'Not authenticated'}, status=401)

def remove_from_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get('product_id')

        order = Order.objects.get(customer=request.user.customer, complete=False)
        item  = OrderItem.objects.get(order=order, product_id=product_id)

        # decrement or remove
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

        cart_count = sum([item.quantity for item in order.orderitem_set.all()])
        return JsonResponse({'cart_count': cart_count})
    
    return JsonResponse({'error': 'Not authenticated'}, status=401)

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    data = get_cart_data(request)
    cart_items = data['cart_items']

    context = {
        'product': product,
        'cart_items': cart_items,
    }   
    return render(request, 'store/product_detail.html', context)

def update_session_cart(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = {}

    product_id = data.get('product_id')
    action = data.get('action')

    if not product_id or not action:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart = request.session['cart']
    product_id_key = str(product_id)

    try:
        product = Product.objects.get(id=product_id)
        current_qty = cart.get(product_id_key, 0)
        
        if action == 'add':
            if product.stock_count > current_qty:
                cart[product_id_key] = current_qty + 1
            else:
                return JsonResponse({'error': 'Not enough stock available'}, status=400)
        elif action == 'remove':
            if current_qty > 1:
                cart[product_id_key] = current_qty - 1
            else:
                del cart[product_id_key]
        
        request.session.modified = True
        cart_count = sum(cart.values())
        return JsonResponse({'cart_count': cart_count})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

def check_email_availability(request):
    email = request.GET.get('email', None)
    if email:
        exists = User.objects.filter(email__iexact=email).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'No email provided'}, status=400)
