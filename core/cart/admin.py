from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline admin configuration for CartItem.
    """

    model = CartItem
    extra = 1  # Number of empty CartItem forms shown by default


class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Cart model.
    """

    list_display = (
        "user",
        "created_at",
        "updated_at",
        "total_items",
        "total_price",
    )
    inlines = [CartItemInline]

    def total_items(self, obj):
        """
        Return the total number of items in the cart.
        """
        return obj.total_items()

    total_items.short_description = "Total Items"

    def total_price(self, obj):
        """
        Return the total price of all items in the cart.
        """
        return obj.total_price()

    total_price.short_description = "Total Price"


class CartItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CartItem model.
    """

    list_display = (
        "cart",
        "product",
        "quantity",
        "subtotal",
    )

    def subtotal(self, obj):
        """
        Return the subtotal price for the cart item.
        """
        return obj.subtotal()

    subtotal.short_description = "Subtotal"


# Register models with custom admin configurations
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
