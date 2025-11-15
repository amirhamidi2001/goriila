from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from blog.models import Category, Post, Comment
from blog.forms import CommentForm
from blog.views import PostListView, PostDetailView

User = get_user_model()


class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="test@example.com", password="1234", is_verified=True
        )

        self.post = Post.objects.create(
            title="Test Post", author=self.user, content="Test content"
        )

    def test_category_str(self):
        cat = Category.objects.create(name="Tech")
        self.assertEqual(str(cat), "Tech")

    def test_post_str(self):
        self.assertEqual(str(self.post), "Test Post")

    def test_comment_str(self):
        comment = Comment.objects.create(
            post=self.post, name="John", email="john@example.com", comment="Nice"
        )
        self.assertEqual(str(comment), f"Comment by John on {self.post.title}")

    def test_get_absolute_url(self):
        self.assertEqual(self.post.get_absolute_url(), f"/blog/post/{self.post.pk}/")

    def test_comment_form_valid(self):
        form = CommentForm(
            data={
                "name": "John",
                "email": "john@example.com",
                "website": "https://example.com",
                "comment": "Nice!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)

    def test_post_list_url_resolves(self):
        url = reverse("blog:post-list")
        self.assertEqual(resolve(url).func.view_class, PostListView)

    def test_post_detail_url_resolves(self):
        url = reverse("blog:post-detail", kwargs={"pk": self.post.pk})
        self.assertEqual(resolve(url).func.view_class, PostDetailView)

    def test_post_detail_requires_login(self):
        url = reverse("blog:post-detail", kwargs={"pk": self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertIn("/login", response.url.lower())

    def test_post_detail_view_authenticated(self):
        self.client.login(email="test@example.com", password="1234")
        url = reverse("blog:post-detail", kwargs={"pk": self.post.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["post"], self.post)
        self.assertIn("form", response.context)
        self.assertIn("comments", response.context)

    def test_post_view_count_increment(self):
        self.assertEqual(self.post.counted_views, 0)

        self.client.login(email="test@example.com", password="1234")
        self.client.get(reverse("blog:post-detail", kwargs={"pk": self.post.pk}))

        self.post.refresh_from_db()
        self.assertEqual(self.post.counted_views, 1)

    def test_comment_submission(self):
        self.client.login(email="test@example.com", password="1234")
        url = reverse("blog:post-detail", kwargs={"pk": self.post.pk})

        data = {
            "name": "John",
            "email": "john@example.com",
            "website": "https://example.com",
            "comment": "Nice!",
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.comment, "Nice!")
