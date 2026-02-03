from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem
import json


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=5000,
            stock_count=10
        )

    def test_product_detail_404(self):
        response = self.client.get(reverse('product_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_guest_update_session_cart_add(self):
        response = self.client.post(
            reverse('update_session_cart'),
            data=json.dumps({'product_id': self.product.id, 'action': 'add'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn(str(self.product.id), session.get('cart', {}))

    def test_authenticated_add_to_cart(self):
        user = User.objects.create_user(username='tester', password='testpass123')
        self.client.login(username='tester', password='testpass123')

        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps({'product_id': self.product.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(customer=user.customer, complete=False)
        order_item = OrderItem.objects.get(order=order, product=self.product)
        self.assertEqual(order_item.quantity, 1)
