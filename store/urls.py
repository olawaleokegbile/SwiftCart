from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('store/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-complete/', views.order_complete, name='order_complete'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('guest_order_summary/', views.guest_order_summary, name='guest_order_summary'),
    path('update_session_cart/', views.update_session_cart, name='update_session_cart'), 
] 