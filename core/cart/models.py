from django.db import models
from shop.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Cart(models.Model):
    """
    Shopping cart model that belongs to a user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_items(self):
        """Return total quantity of items in the cart."""
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        """Return total cost of all items in the cart."""
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart({self.user.email})"

    def get_total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """
    Represents a single product inside a cart with a quantity.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")

    def subtotal(self):
        """Return price * quantity for this item."""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.get_price() * self.quantity