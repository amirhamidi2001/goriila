from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Form for submitting review on shop product.
    """

    class Meta:
        model = Review
        fields = ["name", "email", "website", "review"]
