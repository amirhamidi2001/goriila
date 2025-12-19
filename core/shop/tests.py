from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from shop.models import Brand, Category, Product, ProductImage, Review, Wishlist

User = get_user_model()


class BrandModelTest(TestCase):
    def test_create_brand(self):
        brand = Brand.objects.create(name="TestBrand")
        self.assertEqual(str(brand), "TestBrand")
        self.assertEqual(brand.slug, "testbrand")


class CategoryModelTest(TestCase):
    def test_create_category(self):
        parent = Category.objects.create(name="ParentCategory")
        child = Category.objects.create(name="ChildCategory", parent=parent)
        self.assertEqual(str(child), "ChildCategory")
        self.assertEqual(child.full_path, "ParentCategory > ChildCategory")
        self.assertEqual(child.slug, "childcategory")


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="TestCategory")
        self.brand = Brand.objects.create(name="TestBrand")

    def test_create_product(self):
        product = Product.objects.create(
            name="TestProduct",
            category=self.category,
            brand=self.brand,
            price=1000,
            discount=10,
            stock=5,
        )
        self.assertEqual(str(product), "TestProduct")
        self.assertTrue(product.in_stock)
        self.assertEqual(product.get_price(), Decimal("900"))
        self.assertEqual(product.discount_amount, Decimal("100"))
        self.assertEqual(product.slug, "testproduct")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com")
        self.category = Category.objects.create(name="TestCategory")
        self.product = Product.objects.create(
            name="TestProduct", category=self.category, price=1000
        )

    def test_create_review(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            name="John",
            email="john@example.com",
            review="Great product!",
        )
        self.assertEqual(str(review), f"Review by John on {self.product.name}")


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com")
        self.category = Category.objects.create(name="TestCategory")
        self.product = Product.objects.create(
            name="TestProduct", category=self.category, price=1000
        )

    def test_create_wishlist(self):
        wishlist = Wishlist.objects.create(user=self.user, product=self.product)
        self.assertEqual(str(wishlist), f"{self.user.email} - {self.product.name}")
