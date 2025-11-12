from django.test import TestCase
from django.urls import reverse
from website.models import Contact


class ContactFormTests(TestCase):
    def test_contact_form_post_invalid(self):
        url = reverse("website:contact")
        data = {"email": "", "subject": "", "message": ""}  # missing required fields
        response = self.client.post(url, data)
        response.render()
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("subject", form.errors)
        self.assertIn("message", form.errors)


class WebsiteViewTests(TestCase):
    def test_404_view(self):
        response = self.client.get("/non-existing-url/")
        self.assertTemplateUsed(response, "website/404.html")
        self.assertEqual(response.status_code, 404)
