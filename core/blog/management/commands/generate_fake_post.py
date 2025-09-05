from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random

from accounts.models import User
from blog.models import Post, Category
from taggit.models import Tag


class Command(BaseCommand):
    """
    Django management command to generate fake blog posts.
    """

    help = "Generate fake blog posts with tags"

    def handle(self, *args, **kwargs):
        fake = Faker()

        authors = list(User.objects.all())
        if not authors:
            self.stdout.write(
                self.style.ERROR("No users found. Please create authors first.")
            )
            return

        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(
                self.style.ERROR("No categories found. Please create some categories.")
            )
            return

        post_count = random.randint(30, 50)
        self.stdout.write(f"Creating {post_count} fake blog posts...")

        for _ in range(post_count):
            post = Post.objects.create(
                title=fake.sentence(nb_words=6),
                author=random.choice(authors),
                status=random.choice([True, False]),
                content=fake.paragraph(nb_sentences=10),
                counted_views=random.randint(0, 500),
                login_require=random.choice([True, False]),
                published_at=fake.date_time_between(
                    start_date="-1y", end_date="now", tzinfo=timezone.utc
                ),
            )

            post.category.set(
                random.sample(categories, random.randint(1, min(3, len(categories))))
            )

            for _ in range(random.randint(2, 5)):
                tag_name = fake.word()
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {post_count} posts!")
        )
