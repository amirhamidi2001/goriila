from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
import random

from shop.models import Category, Brand, Product, ProductImage


class Command(BaseCommand):
    help = "🛒 Generate fake eCommerce data (categories, brands, products, product images)"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Step 1: Categories
        if not Category.objects.exists():
            self.stdout.write("📂 Creating categories and subcategories...")
            parent_cats = []
            for _ in range(5):
                title = fake.unique.word().capitalize()
                parent = Category.objects.create(
                    title=title, slug=slugify(title)
                )
                parent_cats.append(parent)

                # Create 2–3 subcategories each
                for _ in range(random.randint(2, 3)):
                    sub_title = fake.unique.word().capitalize()
                    Category.objects.create(
                        title=sub_title,
                        slug=slugify(sub_title),
                        parent=parent,
                    )
        categories = list(Category.objects.all())
        self.stdout.write(self.style.SUCCESS(f"✅ Categories ready: {len(categories)}"))

        # Step 2: Brands
        if not Brand.objects.exists():
            self.stdout.write("🏷️ Creating brands...")
            for _ in range(10):
                title = fake.unique.company()
                Brand.objects.create(
                    title=title,
                    slug=slugify(title),
                    logo=None,  # Placeholder, or set a default logo
                )
        brands = list(Brand.objects.all())
        self.stdout.write(self.style.SUCCESS(f"✅ Brands ready: {len(brands)}"))

        # Step 3: Products
        product_count = random.randint(30, 50)
        self.stdout.write(f"🛍️ Creating {product_count} fake products...")

        for _ in range(product_count):
            title = fake.unique.sentence(nb_words=3).replace(".", "")
            product = Product.objects.create(
                title=title,
                slug=slugify(title),
                description=fake.paragraph(nb_sentences=5),
                price=round(random.uniform(10, 500), 2),
                category=random.choice(categories),
                brand=random.choice(brands),
                weight=random.randint(500, 5000),
                available=random.choice([True, True, False]),  # mostly available
                stock=random.randint(0, 100),
            )

            # Step 4: Product Images (1–3 per product)
            for _ in range(random.randint(1, 3)):
                ProductImage.objects.create(
                    product=product,
                    alt=fake.word(),
                    image="shop/default.jpg",  # ✅ Use placeholder
                )

        self.stdout.write(self.style.SUCCESS(f"🎉 Created {product_count} products with images!"))
