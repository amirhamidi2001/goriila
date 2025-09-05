from django.contrib import admin
from website.models import Contact, Newsletter


class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for managing website contact.
    """

    date_hierarchy = "created_at"
    list_display = ("name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_filter = ("created_at", "email")
    readonly_fields = ("created_at", "updated_at")


class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin interface for managing website newsletter.
    """

    list_display = ("email",)
    search_fields = ("email",)
    list_filter = ("email",)


admin.site.register(Contact, ContactAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
