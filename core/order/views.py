from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Order, OrderItem, Address
from .forms import CheckoutForm
from cart.models import Cart
from cart.cart import CartSession


@method_decorator(login_required, name="dispatch")
class CheckoutView(LoginRequiredMixin, CreateView):
    """
    View for handling the checkout process and creating new orders.
    """

    model = Order
    form_class = CheckoutForm
    template_name = "order/checkout.html"
    success_url = reverse_lazy("order:confirmation")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch method to perform pre-checks before processing the view.
        """
        # Check if user has registered an address
        if not Address.objects.filter(user=request.user).exists():
            messages.warning(request, "لطفاً ابتدا آدرس خود را ثبت کنید")
            return redirect("dashboard:addresses")

        # Check if user has a cart with items
        try:
            self.cart = Cart.objects.get(user=request.user)
            if not self.cart.items.exists():
                raise Cart.DoesNotExist
        except Cart.DoesNotExist:
            messages.warning(request, "سبد خرید شما خالی است")
            return redirect("cart:cart-summary")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Extend form kwargs to pass the current user to the form.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add cart and pricing information to template context.
        """
        context = super().get_context_data(**kwargs)

        # Calculate order totals
        subtotal = self.cart.get_total_price()
        shipping_cost = self.cart.get_shipping_cost()
        total = subtotal + shipping_cost

        context.update(
            {
                "cart": self.cart,
                "subtotal": subtotal,
                "shipping_cost": shipping_cost,
                "total": total,
                "bank_card_number": "6219 8619 2157 4926",
                "bank_account_holder": "فروشگاه گوریلا",
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Process valid form submission and create order with atomic transaction.
        """
        # Get selected shipping address from form
        shipping_address = form.cleaned_data["shipping_address"]

        # Calculate order totals
        subtotal = self.cart.get_total_price()
        shipping_cost = self.cart.get_shipping_cost()
        total = subtotal + shipping_cost

        # Create order instance with user and totals
        order = form.save(commit=False)
        order.user = self.request.user

        # Add shipping address details to order
        order.shipping_full_name = shipping_address.full_name
        order.shipping_phone = shipping_address.phone
        order.shipping_address_line1 = shipping_address.address_line1
        order.shipping_address_line2 = shipping_address.address_line2
        order.shipping_city = shipping_address.city
        order.shipping_state = shipping_address.state
        order.shipping_postal_code = shipping_address.postal_code
        order.shipping_country = shipping_address.country

        # Set order pricing
        order.subtotal = subtotal
        order.shipping_cost = shipping_cost
        order.total = total
        order.save()

        # Create order items from cart items
        for item in self.cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.get_price(),
                quantity=item.quantity,
                subtotal=item.get_total_price(),
            )

        # Clear user's cart after successful order
        self.cart.items.all().delete()
        CartSession(self.request.session).clear()

        # Store order ID in session for confirmation page
        self.request.session["last_order_id"] = order.id
        messages.success(self.request, "سفارش شما با موفقیت ثبت شد")

        return redirect(self.success_url)


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    """
    View for displaying order confirmation details after successful checkout.
    """

    model = Order
    template_name = "order/order_confirmation.html"
    context_object_name = "order"

    def get_object(self):
        """
        Retrieve order object from session-stored order ID.
        """
        order_id = self.request.session.get("last_order_id")
        if not order_id:
            messages.warning(self.request, "سفارشی برای نمایش یافت نشد")
            return redirect("shop:product-list")

        # Remove order ID from session to prevent re-access
        del self.request.session["last_order_id"]

        # Retrieve order ensuring it belongs to current user
        return get_object_or_404(Order, id=order_id, user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Extend template context with additional order information.
        """
        context = super().get_context_data(**kwargs)
        # Additional context can be added here if needed
        return context
