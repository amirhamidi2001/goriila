from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, Address


class ProfileInline(admin.StackedInline):
    """
    Inline display for the user's Profile model.
    """

    model = Profile
    can_delete = False
    verbose_name_plural = _("Profile")
    fk_name = "user"
    fields = (
        "first_name",
        "last_name",
        "phone_number",
        "image",
        "address",
        "created_date",
        "updated_date",
    )
    readonly_fields = ("created_date", "updated_date")


class AddressInline(admin.TabularInline):
    """
    Inline display for the user's Address model.
    """

    model = Address
    extra = 0
    fields = ("address_line", "is_default", "created_date")
    readonly_fields = ("created_date",)
    verbose_name = _("Address")
    verbose_name_plural = _("Addresses")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User model configuration for Django admin.
    """

    inlines = [ProfileInline, AddressInline]

    list_display = (
        "email",
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
        "type",
        "created_date",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "is_verified", "type")
    search_fields = ("email", "user_profile__first_name", "user_profile__last_name")
    ordering = ("-created_date",)
    readonly_fields = ("created_date", "updated_date")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("User Type"), {"fields": ("type",)}),
        (
            _("Important dates"),
            {"fields": ("last_login", "created_date", "updated_date")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "type",
                ),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        """Show inlines only for existing users."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Separate admin interface for Profiles (optional if inline used).
    """

    list_display = ("user", "get_fullname", "phone_number", "created_date")
    search_fields = ("user__email", "first_name", "last_name", "phone_number")
    readonly_fields = ("created_date", "updated_date")
    ordering = ("-created_date",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin configuration for Address model.
    """

    list_display = ("user", "short_address", "is_default", "created_date")
    list_filter = ("is_default",)
    search_fields = ("user__email", "address_line")
    readonly_fields = ("created_date",)
    ordering = ("-is_default", "-created_date")

    def short_address(self, obj):
        """Return a short version of the address."""
        return (
            f"{obj.address_line[:50]}..."
            if len(obj.address_line) > 50
            else obj.address_line
        )

    short_address.short_description = _("address")
