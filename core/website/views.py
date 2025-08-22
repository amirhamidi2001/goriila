from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from website.forms import ContactForm


class IndexView(TemplateView):
    template_name = "website/index.html"


class AboutView(TemplateView):
    template_name = "website/about-us.html"


class ContactView(FormView):
    """
    The ContactView class handles the display and processing of the contact form.
    """

    template_name = "website/contact.html"
    form_class = ContactForm
    success_url = "/contact/"

    def form_valid(self, form):
        """
        If the form is valid, save it and add a success message.
        """
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, "پیام شما با موفقیت ارسال شد"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, add an error message.
        """
        messages.add_message(self.request, messages.ERROR, "ارسال پیام نا موفق بود")
        return super().form_invalid(form)
