from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

from blog.models import Category, Post, Comment

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with fake blog data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting fake data generation...")

        categories = []
        for _ in range(10):
            cat_name = fake.word().capitalize()
            category, created = Category.objects.get_or_create(name=cat_name)
            categories.append(category)
        self.stdout.write(self.style.SUCCESS("Created 10 categories."))

        author, _ = User.objects.get_or_create(
            email="Admin@gmail.com", defaults={"email": "test@example.com"}
        )
        author.set_password("password123")
        author.save()

        posts = []
        for _ in range(50):
            post = Post.objects.create(
                title=fake.sentence(nb_words=6),
                author=author,
                status=random.choice([True, False]),
                content=fake.paragraph(nb_sentences=10),
                counted_views=random.randint(0, 1000),
                login_require=random.choice([True, False]),
                published_at=fake.date_time_this_year(),
            )
            post.category.set(random.sample(categories, random.randint(1, 3)))
            for _ in range(random.randint(1, 5)):
                post.tags.add(fake.word())
            posts.append(post)
        self.stdout.write(self.style.SUCCESS("Created 50 posts."))

        for _ in range(100):
            Comment.objects.create(
                post=random.choice(posts),
                name=fake.name(),
                email=fake.email(),
                website=fake.url(),
                comment=fake.paragraph(nb_sentences=3),
                approved=random.choice([True, False]),
            )
        self.stdout.write(self.style.SUCCESS("Created 100 comments."))

        self.stdout.write(self.style.SUCCESS("Fake data generation completed!"))
