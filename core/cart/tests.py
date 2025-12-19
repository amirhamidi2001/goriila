from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from shop.models import Product, Category
from cart.models import Cart, CartItem

User = get_user_model()


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="cartuser@example.com", password="pass123"
        )
        self.category = Category.objects.create(name="TestCategory")
        self.product1 = Product.objects.create(
            name="Product1", category=self.category, price=1000, stock=10, weight=2
        )
        self.product2 = Product.objects.create(
            name="Product2", category=self.category, price=2000, stock=5, weight=3
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_str(self):
        self.assertEqual(str(self.cart), f"Cart({self.user.email})")

    def test_add_items_and_totals(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)

        self.assertEqual(self.cart.total_items(), 3)
        self.assertEqual(self.cart.get_total_items(), 3)
        # Product1: 1000*2 + Product2: 2000*1 = 4000
        self.assertEqual(self.cart.total_price(), 4000)
        self.assertEqual(self.cart.get_total_price(), 4000)
        # Weight: Product1: 2*2 + Product2: 3*1 = 7
        self.assertEqual(self.cart.get_total_weight(), 7)
        # Shipping: 7 * 100 = 700
        self.assertEqual(self.cart.get_shipping_cost(), Decimal("700"))

    def test_cartitem_str_and_subtotal(self):
        item = CartItem.objects.create(
            cart=self.cart, product=self.product1, quantity=3
        )
        self.assertEqual(str(item), "Product1 x 3")
        self.assertEqual(item.subtotal(), 3000)
        self.assertEqual(item.get_total_price(), 3000)
