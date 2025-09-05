from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """
    Form for submitting comments on blog posts.
    """

    class Meta:
        model = Comment
        fields = ["name", "email", "website", "comment"]
