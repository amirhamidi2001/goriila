from decimal import Decimal
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from shop.models import Product, Category
from order.models import Address, Order, OrderItem

User = get_user_model()


class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="addressuser@example.com", password="pass123"
        )

    def test_create_address(self):
        address = Address.objects.create(
            user=self.user,
            label="Home",
            full_name="John Doe",
            phone="09123456789",
            address_line1="Street 1",
            city="Tehran",
            state="Tehran",
            postal_code="12345",
        )
        self.assertTrue(address.is_default)
        self.assertEqual(str(address), "Home - Tehran, Tehran")
        self.assertIn("Street 1", address.get_full_address())
        self.assertIn("Tehran", address.get_short_address())


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="orderuser@example.com", password="pass123"
        )
        self.category = Category.objects.create(name="TestCategory")
        self.product = Product.objects.create(
            name="TestProduct", category=self.category, price=1000, stock=10, weight=2
        )
        self.payment_receipt = SimpleUploadedFile(
            "receipt.jpg", b"file_content", content_type="image/jpeg"
        )

    def test_create_order_and_item(self):
        order = Order.objects.create(
            user=self.user,
            shipping_full_name="John Doe",
            shipping_phone="09123456789",
            shipping_address_line1="Street 1",
            shipping_city="Tehran",
            shipping_state="Tehran",
            shipping_postal_code="12345",
            shipping_country="ایران",
            payment_receipt=self.payment_receipt,
            subtotal=1000,
            shipping_cost=100,
            total=1100,
        )
        self.assertTrue(order.order_number.startswith("ORD"))
        self.assertEqual(str(order), f"سفارش #{order.order_number}")

        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            product_price=self.product.price,
            quantity=2,
            subtotal=self.product.price * 2,
        )
        self.assertEqual(str(order_item), "TestProduct x 2")
        self.assertEqual(order_item.subtotal, 2000)
