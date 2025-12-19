from django.contrib import admin
from .models import Order, OrderItem

from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin interface for Address model"""

    list_display = [
        "label",
        "user",
        "full_name",
        "city",
        "state",
        "is_default",
        "created_date",
    ]

    list_filter = ["is_default", "address_type", "country", "state", "created_date"]

    search_fields = [
        "user__username",
        "user__email",
        "full_name",
        "label",
        "city",
        "state",
        "postal_code",
        "phone",
    ]

    readonly_fields = ["created_date", "updated_date"]

    fieldsets = (
        (
            "Address Information",
            {"fields": ("user", "label", "address_type", "is_default")},
        ),
        ("Contact Details", {"fields": ("full_name", "phone")}),
        (
            "Address Details",
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )

    list_per_page = 25

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user")

    actions = ["make_default", "make_not_default"]

    def make_default(self, request, queryset):
        """Custom action to set selected addresses as default"""
        updated = 0
        for address in queryset:
            # Remove default from other addresses of the same user
            Address.objects.filter(user=address.user, is_default=True).exclude(
                pk=address.pk
            ).update(is_default=False)

            # Set this address as default
            address.is_default = True
            address.save()
            updated += 1

        self.message_user(
            request, f"{updated} address(es) were successfully set as default."
        )

    make_default.short_description = "Set selected addresses as default"

    def make_not_default(self, request, queryset):
        """Custom action to remove default flag"""
        updated = queryset.update(is_default=False)
        self.message_user(
            request, f"{updated} address(es) were successfully unmarked as default."
        )

    make_not_default.short_description = "Remove default flag from selected addresses"


class OrderItemInline(admin.TabularInline):
    """
    Inline admin display for OrderItem.

    Displays order items within the Order admin page
    in a read-only tabular format.
    """

    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = (
        "product",
        "product_name",
        "product_price",
        "quantity",
        "subtotal",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order model.
    """

    list_display = (
        "order_number",
        "user",
        "status",
        "total",
        "created_date",
    )

    list_filter = ("status", "created_date")

    search_fields = (
        "order_number",
        "user__email",
        "shipping_full_name",
        "shipping_phone",
    )

    readonly_fields = (
        "order_number",
        "user",
        "subtotal",
        "shipping_cost",
        "total",
        "created_date",
        "updated_date",
    )

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "created_date",
                    "updated_date",
                )
            },
        ),
        (
            "آدرس ارسال",
            {
                "fields": (
                    "shipping_full_name",
                    "shipping_phone",
                    "shipping_address_line1",
                    "shipping_address_line2",
                    "shipping_city",
                    "shipping_state",
                    "shipping_postal_code",
                    "shipping_country",
                )
            },
        ),
        (
            "اطلاعات پرداخت",
            {"fields": ("payment_receipt",)},
        ),
        (
            "مبالغ",
            {"fields": ("subtotal", "shipping_cost", "total")},
        ),
        (
            "یادداشت‌ها",
            {"fields": ("notes",)},
        ),
    )

    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        """
        Disable manual creation of orders via admin panel.
        """
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderItem model.
    """

    list_display = (
        "order",
        "product_name",
        "quantity",
        "product_price",
        "subtotal",
    )

    list_filter = ("order__created_date",)

    search_fields = (
        "order__order_number",
        "product_name",
    )

    readonly_fields = (
        "order",
        "product",
        "product_name",
        "product_price",
        "quantity",
        "subtotal",
    )

    def has_add_permission(self, request):
        """
        Prevent adding order items manually.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deleting order items from admin.
        """
        return False
