from typing import Any
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from shop.models import Product
from .cart import CartSession


class BaseCartActionView(View):
    """
    Base view for cart actions that handles common cart operations
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for cart operations.
        """
        self.cart = CartSession(request.session)

        action_result = self.perform_action(request) or {}

        # Merge session cart with database cart for authenticated users
        if request.user.is_authenticated:
            self.cart.merge_session_cart_in_db(request.user)

        response_data = {
            "cart": self.cart.get_cart_dict(),
            "total_quantity": self.cart.get_total_quantity(),
        }
        response_data.update(action_result)

        return JsonResponse(response_data)

    def perform_action(self, request):
        """
        Perform specific cart action. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement perform_action")


class SessionAddProductView(BaseCartActionView):
    """Add a product to the cart session."""

    def perform_action(self, request):
        """
        Add product to cart if it exists and is available.
        """
        product_id = request.POST.get("product_id")
        added = False
        if (
            product_id
            and Product.objects.filter(id=product_id, available=True).exists()
        ):
            added = self.cart.add_product(product_id)

        return {"added": added}


class SessionDecreaseProductQuantityView(BaseCartActionView):
    """Decrease quantity of a product in the cart session."""

    def perform_action(self, request):
        """
        Decrease product quantity by one.
        """
        product_id = request.POST.get("product_id")
        decreased = False
        if product_id:
            decreased = self.cart.decrease_product_quantity(product_id)

        return {"decreased": decreased}


class SessionRemoveProductView(BaseCartActionView):
    """Remove a product completely from the cart session."""

    def perform_action(self, request):
        """
        Remove product from cart.
        """
        product_id = request.POST.get("product_id")
        if product_id:
            self.cart.remove_product(product_id)
        return {}


class SessionUpdateProductQuantityView(BaseCartActionView):
    """Update quantity of a specific product in the cart session."""

    def perform_action(self, request):
        """
        Update product quantity to specified value.
        """
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")
        if product_id and quantity:
            self.cart.update_product_quantity(product_id, quantity)
        return {}


class SessionClearCartView(BaseCartActionView):
    """Remove all items from the cart session."""

    def perform_action(self, request):
        """
        Clear all items from the cart.
        """
        self.cart.clear()
        return {}


class CartSummaryView(TemplateView):
    """
    Display cart summary page with all cart items and pricing information.
    """

    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs: Any):
        """
        Add cart-related data to template context.
        """
        context = super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)

        context.update(
            {
                "cart_items": cart.get_cart_items(),
                "total_quantity": cart.get_total_quantity(),
                "total_payment_price": cart.get_total_payment_amount(),
                "total_discount": cart.get_total_discount_amount(),
                "get_total_price": cart.get_total_price(),
                "shipping_cost": cart.get_shipping_cost(),
            }
        )
        return context
