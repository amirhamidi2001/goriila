from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from .forms import CheckoutForm
from .models import Order, OrderItem, Address
from cart.models import Cart, CartItem
from cart.cart import CartSession

class CheckoutView(LoginRequiredMixin, FormView):
    """View for handling checkout process"""
    
    template_name = 'order/checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('order:order_confirmation')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has cart with items
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            messages.warning(request, 'سبد خرید شما خالی است.')
            return redirect('cart:cart-summary')
        
        # Check if user has at least one address
        if not Address.objects.filter(user=request.user).exists():
            messages.warning(request, 'لطفاً ابتدا یک آدرس اضافه کنید.')
            return redirect('dashboard:addresses')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Add user to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's addresses
        addresses = Address.objects.filter(user=self.request.user).order_by(
            '-is_default', '-created_date'
        )
        context['addresses'] = addresses
        
        # Get cart and calculate totals
        cart = Cart.objects.filter(user=self.request.user).first()
        cart_items = cart.items.select_related('product') if cart else []
        
        # Calculate totals
        subtotal = sum(item.get_total_price() for item in cart_items)
        shipping_cost = Decimal('0')  # You can add shipping calculation logic here
        total_amount = subtotal + shipping_cost
        
        context.update({
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'total_amount': total_amount,
            'item_count': sum(item.quantity for item in cart_items)
        })
        
        return context
    
    def form_valid(self, form):
        """Process valid form and create order"""
        try:
            with transaction.atomic():
                # Get cart
                cart = Cart.objects.filter(user=self.request.user).first()
                if not cart or not cart.items.exists():
                    messages.error(self.request, 'سبد خرید شما خالی است.')
                    return redirect('cart:cart_detail')
                
                # Get selected address
                address_id = form.cleaned_data['shipping_address']
                shipping_address = get_object_or_404(
                    Address,
                    id=address_id,
                    user=self.request.user
                )
                
                # Calculate total
                cart_items = cart.items.select_related('product')
                total_amount = sum(item.get_total_price() for item in cart_items)
                
                # Create order
                order = form.save(commit=False)
                order.user = self.request.user
                order.shipping_address = shipping_address
                order.total_amount = total_amount
                order.status = 'pending'
                order.payment_status = 'pending'
                order.save()
                
                # Create order items from cart
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.title,
                        product_price=cart_item.product.get_price(),
                        quantity=cart_item.quantity
                    )
                
                # Clear cart after successful order
                cart.items.all().delete()
                
                # Store order number in session for confirmation page
                self.request.session['last_order_number'] = order.order_number
                
                messages.success(
                    self.request,
                    f'سفارش شما با موفقیت ثبت شد. شماره سفارش: {order.order_number}'
                )
                
                return redirect('order:order_confirmation', order_number=order.order_number)
                
        except Exception as e:
            messages.error(
                self.request,
                f'خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle invalid form"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class OrderConfirmationView(LoginRequiredMixin, FormView):
    """View for order confirmation page"""
    
    template_name = 'order/order_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get order number from URL or session
        order_number = self.kwargs.get('order_number') or \
                      self.request.session.get('last_order_number')
        
        if order_number:
            order = get_object_or_404(
                Order,
                order_number=order_number,
                user=self.request.user
            )
            context['order'] = order
            
            # Clear session
            if 'last_order_number' in self.request.session:
                del self.request.session['last_order_number']
        
        return context