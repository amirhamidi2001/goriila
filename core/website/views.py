"""Views for the website app."""

from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from website.forms import ContactForm, NewsletterForm


class IndexView(TemplateView):
    """Homepage view."""

    template_name = "website/index.html"


class AboutView(TemplateView):
    """About page view."""

    template_name = "website/about.html"


class ContactView(FormView):
    """Handles display and processing of the contact form."""

    template_name = "website/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("website:contact")

    def form_valid(self, form):
        """If the form is valid, save it and show a success message."""
        form.save()
        messages.success(self.request, "پیام شما با موفقیت ارسال شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, show an error message."""
        messages.error(self.request, "ارسال پیام ناموفق بود.")
        return super().form_invalid(form)


class FAQView(TemplateView):
    """FAQ page view."""

    template_name = "website/faq.html"


class Custom404View(View):
    """Custom 404 error page view."""

    template_name = "website/404.html"

    def get(self, request, exception=None):
        """Render the custom 404 page."""
        return render(request, self.template_name, status=404)
