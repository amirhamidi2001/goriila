from django.db import models


class Contact(models.Model):
    """
    Represents a contact form submission.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Contact model."""

        ordering = ["-created_at"]
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        """Return the contact's name as string representation."""
        return self.name


class Newsletter(models.Model):
    """
    Represents a newsletter subscription.
    """

    email = models.EmailField(unique=True)

    class Meta:
        """Meta options for the Newsletter model."""

        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        """Return the subscriber's email as string representation."""
        return self.email
