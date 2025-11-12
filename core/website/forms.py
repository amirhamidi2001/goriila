from django import forms
from .models import Contact, Newsletter


class ContactForm(forms.ModelForm):
    """
    Form for handling contact submissions.
    """

    class Meta:
        model = Contact
        fields = "__all__"


class NewsletterForm(forms.ModelForm):
    """
    Form for handling newsletter subscriptions.
    """

    class Meta:
        model = Newsletter
        fields = ["email"]
