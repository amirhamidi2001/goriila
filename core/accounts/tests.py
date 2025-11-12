from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationTests(TestCase):
    def test_register_view_post_invalid_password_mismatch(self):
        url = reverse("accounts:register")
        data = {
            "email": "test@example.com",
            "password1": "password123",
            "password2": "password456",
        }
        response = self.client.post(url, data)
        response.render()  # render TemplateResponse to access context
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("password2", form.errors)
        self.assertEqual(
            form.errors["password2"][0], "رمزهای عبور وارد شده با هم مطابقت ندارند."
        )


class UserLoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.user.is_active = True
        self.user.save()

    def test_login_invalid_password(self):
        url = reverse("accounts:login")
        data = {"email": "test@example.com", "password": "wrongpass"}
        response = self.client.post(url, data)
        response.render()
        form = response.context["form"]
        self.assertIn("ایمیل یا رمز عبور اشتباه است.", form.non_field_errors())


class UserModelTests(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(
            email="profiletest@example.com", password="password123"
        )
        # Access the related Profile
        profile = user.user_profile
        self.assertTrue(profile.first_name in ["", None])
        self.assertTrue(profile.last_name in ["", None])
