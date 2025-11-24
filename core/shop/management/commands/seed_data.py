from django.core.management.base import BaseCommand
from faker import Faker
import random
from decimal import Decimal
from shop.models import Brand, Category, Product  # adjust your app name if needed
from django.utils.text import slugify

fake = Faker()


class Command(BaseCommand):
    help = "Seed database with fake Brands, Categories, and Products"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding database..."))

        self.create_brands(10)
        categories = self.create_categories(10)
        brands = list(Brand.objects.all())

        self.create_products(100, categories, brands)

        self.stdout.write(self.style.SUCCESS("Seeding completed."))

    def create_brands(self, count):
        Brand.objects.all().delete()

        for _ in range(count):
            name = fake.company()
            Brand.objects.create(
                name=name,
                slug=slugify(name),
                description=fake.text(max_nb_chars=200),
                website=fake.url(),
                is_active=True,
            )
        print(f"Created {count} Brands.")

    def create_categories(self, count):
        Category.objects.all().delete()
        categories = []

        for _ in range(count):
            name = fake.word().capitalize()
            category = Category.objects.create(
                name=name,
                slug=slugify(name),
                description=fake.text(max_nb_chars=200),
                is_active=True,
            )
            categories.append(category)

        print(f"Created {count} Categories.")
        return categories

    def create_products(self, count, categories, brands):
        Product.objects.all().delete()

        for _ in range(count):
            name = fake.sentence(nb_words=3).replace(".", "")
            price = round(random.uniform(10, 500), 1)
            discount = round(random.uniform(0, 20), 1)

            Product.objects.create(
                name=name,
                slug=slugify(name),
                category=random.choice(categories),
                brand=random.choice(brands),
                description=fake.text(),
                price=Decimal(price),
                discount=Decimal(discount),
                weight=f"{random.randint(100, 5000)}",
                taste=random.choice(
                    ["Vanilla", "Chocolate", "Strawberry", "Mint", None]
                ),
                stock=random.randint(0, 10),
                rating=Decimal(round(random.uniform(0, 5), 1)),
                available=True,
            )

        print(f"Created {count} Products.")
