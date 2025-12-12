from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from .models import Order, OrderItem, Address
from .forms import CheckoutForm
from cart.models import Cart


class CheckoutView(LoginRequiredMixin, CreateView):
    """View for checkout process"""
    
    model = Order
    form_class = CheckoutForm
    template_name = 'order/checkout.html'
    success_url = reverse_lazy('order:order_success')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has saved addresses
        if not Address.objects.filter(user=request.user).exists():
            messages.warning(
                request,
                'لطفاً ابتدا آدرس خود را ثبت کنید'
            )
            return redirect('dashboard:addresses')
        
        # Check if cart exists and has items
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                messages.warning(request, 'سبد خرید شما خالی است')
                return redirect('cart:cart_detail')
        except Cart.DoesNotExist:
            messages.warning(request, 'سبد خرید شما خالی است')
            return redirect('cart:cart_detail')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's cart
        cart = Cart.objects.get(user=self.request.user)
        
        # Calculate order totals
        subtotal = cart.get_total_price()
        shipping_cost = Decimal('9.99')  # Fixed shipping cost
        tax = subtotal * Decimal('0.09')  # 9% tax
        total = subtotal + shipping_cost + tax
        
        context.update({
            'cart': cart,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax': tax,
            'total': total,
            'bank_card_number': '6037-9974-1234-5678',  # Store's bank card
            'bank_account_holder': 'فروشگاه گوریلا',
        })
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        # Get the selected address
        shipping_address = form.cleaned_data['shipping_address']
        
        # Get user's cart
        cart = Cart.objects.get(user=self.request.user)
        
        # Calculate totals
        subtotal = cart.get_total_price()
        shipping_cost = Decimal('9.99')
        tax = subtotal * Decimal('0.09')
        total = subtotal + shipping_cost + tax
        
        # Create order
        order = form.save(commit=False)
        order.user = self.request.user
        
        # Copy shipping address information
        order.shipping_full_name = shipping_address.full_name
        order.shipping_phone = shipping_address.phone
        order.shipping_address_line1 = shipping_address.address_line1
        order.shipping_address_line2 = shipping_address.address_line2
        order.shipping_city = shipping_address.city
        order.shipping_state = shipping_address.state
        order.shipping_postal_code = shipping_address.postal_code
        order.shipping_country = shipping_address.country
        
        # Set order totals
        order.subtotal = subtotal
        order.shipping_cost = shipping_cost
        order.tax = tax
        order.total = total
        order.status = 'pending'
        
        order.save()
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.get_price(),
                quantity=cart_item.quantity,
                subtotal=cart_item.get_total_price()
            )
        
        # Clear the cart
        cart.items.all().delete()
        
        # Store order ID in session for success page
        self.request.session['last_order_id'] = order.id
        
        messages.success(
            self.request,
            f'سفارش شما با موفقیت ثبت شد. شماره سفارش: {order.order_number}'
        )
        
        return redirect(self.get_success_url())


class OrderSuccessView(LoginRequiredMixin, DetailView):
    """View for order success page"""
    
    model = Order
    template_name = 'order/order_success.html'
    context_object_name = 'order'
    
    def get_object(self):
        order_id = self.request.session.get('last_order_id')
        if not order_id:
            return redirect('shop:product_list')
        
        # Clear the session
        del self.request.session['last_order_id']
        
        return get_object_or_404(
            Order,
            id=order_id,
            user=self.request.user
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View for order detail page"""
    
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)